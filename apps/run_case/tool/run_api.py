#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_api.py
@Time: 2022/8/23-15:20
"""

import time
import copy
import json
import asyncio
import jsonpath
import random
import aiohttp
from aiohttp import client_exceptions
from typing import List
from sqlalchemy.orm import Session
from tools import logger, get_cookie, AsyncMySql
# from .extract import extract as my_extract
from tools.read_setting import setting
from apps.template import schemas as temp
from apps.case_service import schemas as service
from apps.case_service import crud as service_crud
from apps.run_case import CASE_STATUS, CASE_RESPONSE, CASE_STATUS_LIST
from apps.api_report.tool import write_api_report
from .check_data import check_customize
from tools import replace_data
from .assert_case import AssertCase
from .run_api_data_processing import DataProcessing, req_info
from .run_api_data_collection import api_detail, ApiReport, CaseStatus


class RunApi:
    def __init__(self):
        timeout = aiohttp.ClientTimeout(total=120)
        self.sees = aiohttp.client.ClientSession(timeout=timeout)
        self.cookies = {}
        self.code = None  # 存验证码数据
        self.extract = None  # 存提取的内容
        self.status = None

    async def fo_service(
            self,
            db: Session,
            case_id: int,
            temp_data: List[temp.TemplateDataOut],
            case_data: List[service.TestCaseData],
            temp_pro: str,
            temp_name: str,
            setting_info_dict: dict
    ):
        """
        集合模板用例和测试数据
        1.识别url，data中的表达式
        2.拿表达式从response里面提取出来值
        """

        random_key = f"{int(time.time() * 1000)}{random.uniform(0, 1)}"

        # 从环境配置里面取数据
        customize = await check_customize(setting_info_dict.get('customize', {}))
        db_config = setting_info_dict.get('db', {})

        # 数据处理
        temp_data = copy.deepcopy(temp_data)
        case_data = copy.deepcopy(case_data)
        data_processing = DataProcessing(db=db, code=self.code, extract=self.extract)  # 请求前的数据处理

        # *响应数据收集，用于数据提取*
        response_data = {'response': [], 'headers': []}

        # 数据收集
        api_detail_list = []  # 接口详情
        CASE_RESPONSE[case_id] = []  # 存放接口返回的数据，用作查看jsonpath引用追踪
        report = ApiReport(total_api=len(temp_data))  # 接口测试报告
        self.status = CaseStatus(case_id=case_id, total=len(temp_data))  # 接口的实时状态
        CASE_STATUS_LIST[random_key] = []  # 用于实时数据

        all_is_fail = False  # 总体的接口结果
        for num in range(len(temp_data)):
            config: dict = copy.deepcopy(dict(case_data[num].config))
            logger.info(f"{'=' * 30}case_id:{case_id},开始请求,number:{num}{'=' * 30}")
            try:
                # 处理jsonpath数据
                url, params, data, case_header, check = await data_processing.processing(
                    case_data=case_data[num],
                    temp_data=temp_data[num],
                    response=response_data['response'],
                    response_headers=response_data['headers'],
                    customize=customize,
                )
            except IndexError:
                await self.sees.close()
                raise IndexError(f'case_id:{case_id},参数提取错误, 请检查用例编号: {num} 的提取表达式')

            # 执行用例前的数据组装
            request_info = req_info(
                url=url,
                params=params,
                data=data,
                case_header=case_header,
                temp_data=temp_data[num],
                cookies=self.cookies
            )

            # 计算check的内容
            await self._check_count(check=check)

            # 轮询执行接口
            res, is_fail, response_time, result, res_json = await self._polling(
                number=num,
                config=config,
                check=check,
                request_info=request_info,
                files=temp_data[num].file_data,
                random_key=random_key,
                db_config=db_config
            )
            logger.debug(f"case_id:{case_id},请求信息: {json.dumps(request_info, indent=2, ensure_ascii=False)}")
            request_info['__data'] = data

            if is_fail:
                all_is_fail = is_fail

            if config['is_login']:
                self.cookies[temp_data[num].host] = await get_cookie(rep_type='aiohttp', response=res)

            # # 从html文本中提取数据
            # if config.get('extract'):
            #     _extract = config['extract']
            #     self.extract = await my_extract(
            #         pattern=_extract[0],
            #         string=await res.text(encoding='utf-8'),
            #         index=_extract[1]
            #     )

            response_data['response'].append(res_json)
            response_data['headers'].append(dict(res.headers))

            # 判断响应结果，调整校验内容收集
            if res.status != check.get('status_code', 9999):
                actual = {'status_code': [res.status]}
            else:
                new_check = copy.deepcopy(check)
                del new_check['status_code']
                actual = {
                    **{'status_code': [res.status]},
                    **{k: jsonpath.jsonpath(res_json, f'$..{k}') for k in new_check if 'sql_' not in k},
                    **{k: [new_check[k][1]] for k in new_check if 'sql_' in k}
                }

            logger.debug(f"case_id:{case_id},响应信息: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
            logger.debug(f"{'=' * 30}case_id:{case_id},结束请求,number:{num}{'=' * 30}")

            # 存当前测试用例的数据，用于查看jsonpath取值数据
            CASE_RESPONSE[case_id].append(
                {
                    'path': url,
                    'params': params,
                    'data': request_info['__data'],
                    'headers': dict(res.headers),
                    'response': res_json,
                }
            )

            # 测试详情数据
            api_detail_list.append(
                api_detail(
                    number=num,
                    case_id=case_id,
                    case_data=case_data[num],
                    temp_data=temp_data[num],
                    res=res,
                    res_json=res_json,
                    response_time=response_time,
                    request_info=request_info,
                    check=check,
                    actual=actual,
                    config=dict(case_data[num].config),
                    is_fail=is_fail,
                    result=result,
                    case_response=CASE_RESPONSE,
                )
            )

            # 填充报告列表信息
            report.report(
                case_id=case_id,
                is_fail=is_fail,
                response_time=response_time,
                config=config,
                all_is_fail=all_is_fail,
            )

            config['sleep'] = 0.3
            await asyncio.sleep(config['sleep'])

            # 失败停止的判断
            if setting['global_fail_stop'] and is_fail and config.get('fail_stop'):
                CASE_STATUS[random_key]['run'] = False
                logger.info(f"case_id:{case_id},编号: {num} 校验错误-退出执行")
                await self.sees.close()
                break

            if config.get('stop'):
                CASE_STATUS[random_key]['run'] = False
                logger.info(f"case_id:{case_id},number:{num} 接口配置信息stop = {config['stop']}, 停止后续接口请求")
                await self.sees.close()
                break

            if CASE_STATUS[random_key]['stop']:
                CASE_STATUS[random_key]['run'] = False
                logger.info(f"case_id:{case_id},number:{num} 手动停止执行")
                asyncio.create_task(self._del_case_status(random_key))
                await self.sees.close()
                break

        await self.sees.close()
        # 循环结束后，将最后一个接口信息运行状态设置为false
        if CASE_STATUS_LIST.get(random_key):
            CASE_STATUS_LIST[random_key][-1]['run'] = False

        asyncio.create_task(self._del_case_status(random_key))  # 延时删除
        await write_api_report(db=db, api_report=report.api_report, api_detail=api_detail_list)  # 存报告

        case_info = await service_crud.get_case_info(db=db, case_id=case_id)
        logger.info(f"用例: {temp_pro}-{temp_name}-{case_info[0].case_name} 执行完成, 序号: {case_info[0].run_order}")
        return f"{temp_pro}-{temp_name}-{case_info[0].case_name}", report.api_report

    async def _polling(
            self,
            number: int,
            config: dict,
            check: dict,
            request_info: dict,
            files,
            random_key: str,
            db_config: dict
    ):
        """
        轮询执行接口
        :param config:
        :param check:
        :param request_info:
        :param files:
        :param random_key:
        :param db_config:
        :return:
        """

        # check = copy.deepcopy(check)
        polling_fail = False  # 标记是否失败
        num = 0
        res_json = {}
        sleep = config['sleep']
        while True:
            logger.info(f"{num + 1}次: {request_info['url']}")

            start_time = time.monotonic()
            res = await self.sees.request(**request_info, allow_redirects=False)
            response_time = time.monotonic() - start_time

            status_code = check['status_code']

            result = []
            is_fail = await AssertCase.assert_case(
                k='status_code',
                compare='==',
                expect=status_code,
                actual=res.status,
                result=result
            )
            if is_fail:
                polling_fail = True

                # 状态码错误，后面未校验的内容自动设置为跳过
                del check['status_code']
                result += [{
                    "key": k,
                    "actual": '-',
                    "compare": v[0] if not isinstance(v, (str, int, float, bool, dict)) else '==',
                    "expect": v[1] if not isinstance(v, (str, int, float, bool, dict)) else v,
                    "is_fail": 'skip',
                } for k, v in check.items()]
                check['status_code'] = status_code

                # 因为这里校验了状态码，所以后面的内容都不用校验了，但需要添加上测试接口状态
                self.set_status(
                    num=num,
                    number=number,
                    status_code=res.status,
                    response_time=response_time,
                    is_fail=is_fail,
                    config=config,
                    request_info=request_info,
                    res_json=res_json,
                    check=check,
                    result=result,
                    files=files,
                    random_key=random_key
                )
                break

            del check['status_code']

            try:
                res_json = await res.json(content_type='application/json' if not files else None) or {}
            except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError):
                res_json = {}

            for k, v in check.items():
                # 从数据库获取需要的值
                if isinstance(v, list) and 'sql_' == k[:4]:
                    sql_data = await self._sql_data(v[1], db_config)
                    is_fail = await AssertCase.assert_case(
                        k=k,
                        compare='==',
                        expect=v[0],
                        actual=sql_data[0],
                        result=result
                    )
                    if is_fail:
                        polling_fail = True

                    check[k][1] = sql_data[0]
                    continue

                # 从响应信息获取需要的值
                value = jsonpath.jsonpath(res_json, f'$..{k}')
                if value:
                    value = value[0]
                # 校验结果
                is_fail = await AssertCase.assert_case(
                    k=k,
                    compare='==' if isinstance(v, (str, int, float, bool, dict)) else v[0],
                    expect=v if isinstance(v, (str, int, float, bool, dict)) else v[1],
                    actual=value,
                    result=result
                )

                if is_fail:
                    polling_fail = True

            logger.debug(f"实际-{result}")
            logger.debug(f"预期-{check}")

            self.set_status(
                num=num,
                number=number,
                status_code=res.status,
                response_time=response_time,
                is_fail=is_fail,
                config=config,
                request_info=request_info,
                res_json=res_json,
                check=check,
                result=result,
                files=files,
                random_key=random_key
            )

            if CASE_STATUS[random_key]['stop']:
                CASE_STATUS[random_key]['run'] = False
                asyncio.create_task(self._del_case_status(random_key))
                break

            check['status_code'] = status_code
            if len(check) == len([x for x in result if x['is_fail'] == 'pass']):
                polling_fail = False
                break
            else:
                polling_fail = True

            if sleep < 5:
                break

            await asyncio.sleep(5)
            sleep -= 5
            num += 1

        return res, polling_fail, response_time, result, res_json

    def set_status(
            self,
            num,
            number,
            status_code,
            response_time,
            is_fail,
            config,
            request_info,
            res_json,
            check,
            result,
            files,
            random_key
    ):
        self.status.status(
            num=num,
            number=number,
            status_code=status_code,
            response_time=response_time,
            is_fail=is_fail,
            config=config,
            request_info=request_info,
            res_json=res_json,
            check=check,
            result=result,
            files=files,
            stop=CASE_STATUS.get(random_key, {}).get('stop', False)
        )
        CASE_STATUS[random_key] = copy.deepcopy(self.status.case_status)
        CASE_STATUS_LIST[random_key].append(copy.deepcopy(self.status.case_status))

    @staticmethod
    async def _sql_data(sql: str, db_config: dict):
        """
        从数据库查询数据
        :param sql:
        :param db_config:
        :return:
        """
        if db_config.get('name'):
            del db_config['name']

        async with AsyncMySql(db_config) as s:
            sql_data = await s.select(sql=sql)
            return [x[0] for x in sql_data] if sql_data else False

    @staticmethod
    async def _del_case_status(random_key):
        """
        延迟删除用例运行状态
        :param random_key:
        :return:
        """
        await asyncio.sleep(5)
        if CASE_STATUS.get(random_key):
            logger.info(f"延迟删除:{random_key},成功")
            del CASE_STATUS[random_key]

    @staticmethod
    async def _check_count(check: dict):
        """
        对校验数据进行加减乘除
        :param check:
        :return:
        """
        for k, v in check.items():
            for x in replace_data.COUNT:
                if isinstance(v, list):
                    if isinstance(v[1], str) and x in v[1]:
                        try:
                            v[1] = eval(v[1])
                            check[k] = v
                        except NameError:
                            pass
                if isinstance(v, str):
                    if x in v:
                        try:
                            check[k] = eval(v)
                        except NameError:
                            pass
