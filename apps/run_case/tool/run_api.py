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
import base64
import asyncio
import jsonpath
import random
# import ddddocr
import aiohttp
from aiohttp import FormData
from aiohttp import client_exceptions
from typing import List
from sqlalchemy.orm import Session
from tools import logger, get_cookie, AsyncMySql
from tools.faker_data import FakerData
# from .extract import extract as my_extract
from tools.read_setting import setting
from apps.template import schemas as temp
from apps.case_service import schemas as service
from apps.case_service import crud as service_crud
from apps.case_service.tool import js_count
from apps.run_case import CASE_STATUS, CASE_RESPONSE, CASE_STATUS_LIST
from apps.api_report.tool import write_api_report
from .check_data import check_customize
from tools import replace_data
from .assert_case import AssertCase


class RunApi:
    def __init__(self):
        timeout = aiohttp.ClientTimeout(total=120)
        self.sees = aiohttp.client.ClientSession(timeout=timeout)
        self.cookies = {}
        self.code = None  # 存验证码数据
        self.extract = None  # 存提取的内容
        self.fk = FakerData()

        # 用例执行的实时状态
        self.case_status = {
            'case_id': 0,
            'number': 0,
            'total': 0,
            'stop': False,
            'success': 0,
            'fail': 0,
            'sleep': 0,
            'actual': {},
            'expect': {},
            'request_info': {},
            'response_info': {},
            'time': 0,
            'time_str': '',
            'is_fail': False,
            'status_code': None,
            'run_time': 0,
            'is_login': False,
            'run': True
        }

        # 测试报告列表数据
        self.api_report = {
            "case_id": 0,
            "is_fail": False,
            "run_number": 0,
            "run_api": 0,
            "total_api": 0,
            "initiative_stop": False,
            "fail_stop": False,
            "success": 0,
            "fail": 0,
            "total_time": 0,
            "max_time": 0,
            "avg_time": 0,
        }

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
        2.拿到值，直接替换
        """

        random_key = f"{int(time.time() * 1000)}{random.uniform(0, 1)}"

        # 从环境配置里面取数据
        customize = await check_customize(setting_info_dict.get('customize', {}))
        db_config = setting_info_dict.get('db', {})

        self.case_status['case_id'] = case_id
        self.case_status['total'] = len(temp_data)
        CASE_STATUS_LIST[random_key] = []

        temp_data = copy.deepcopy(temp_data)
        case_data = copy.deepcopy(case_data)
        CASE_STATUS[random_key] = copy.deepcopy(self.case_status)

        # *提取数据的收集*
        response = []
        response_headers = []
        # 接口详情
        api_detail_list = []
        # 总体的接口结果
        all_is_fail = False
        # 测试响应结果
        CASE_RESPONSE[case_id] = []
        for num in range(len(temp_data)):
            # 测试报告详情数据
            api_detail = {
                'status': '',
                'method': '',
                'host': '',
                'path': '',
                'run_time': '',
                'request_info': {},
                'response_info': {},
                'expect_info': {},
                'actual_info': {},
                'jsonpath_info': {},
                'conf_info': {},
                'other_info': {}
            }

            config: dict = copy.deepcopy(dict(case_data[num].config))
            logger.debug(f"{'=' * 30}case_id:{case_id},开始请求,number:{num}{'=' * 30}")
            try:
                # 识别url表达式
                url = await replace_data.replace_url(
                    db=db,
                    old_str=f"{temp_data[num].host}{case_data[num].path}",
                    response=response,
                    response_headers=response_headers,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别params表达式
                params = await replace_data.replace_params_data(
                    db=db,
                    data=case_data[num].params,
                    response=response,
                    response_headers=response_headers,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别data表达式
                data = await replace_data.replace_params_data(
                    db=db,
                    data=case_data[num].data,
                    response=response,
                    response_headers=response_headers,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别headers中的表达式
                case_header = await replace_data.replace_params_data(
                    db=db,
                    data=case_data[num].headers,
                    response=response,
                    response_headers=response_headers,
                    faker=self.fk,
                    customize=customize
                )
                # 识别校验的数据
                check = await replace_data.replace_params_data(
                    db=db,
                    data=case_data[num].check,
                    response=response,
                    response_headers=response_headers,
                    faker=self.fk,
                    customize=customize
                )

            except IndexError:
                await self.sees.close()
                raise IndexError(f'case_id:{case_id},参数提取错误, 请检查用例编号: {num} 的提取表达式')

            # 替换headers中的内容
            headers = await self._replace_headers(
                tmp_header=temp_data[num].headers,
                case_header=case_header,
                tmp_host=temp_data[num].host,
                tmp_file=temp_data[num].file
            )

            request_info = {
                'url': url,
                'method': temp_data[num].method,
                'headers': headers,
                'params': params,
                f"{'json' if temp_data[num].json_body == 'json' else 'data'}": data,
            }

            logger.debug(f"case_id:{case_id},请求信息: {json.dumps(request_info, indent=2, ensure_ascii=False)}")

            # 计算check的内容
            await self._check_count(check=check)

            # 轮询执行接口
            res, is_fail, response_time, result = await self._polling(
                case_id=case_id,
                sleep=config['sleep'],
                check=check,
                request_info=request_info,
                files=temp_data[num].file_data,
                random_key=random_key,
                db_config=db_config
            )
            request_info['__data'] = data

            if is_fail:
                all_is_fail = is_fail

            CASE_STATUS[random_key]['number'] = num
            CASE_STATUS[random_key]['time'] = int(time.time() * 1000)
            CASE_STATUS[random_key]['time_str'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            CASE_STATUS[random_key]['status_code'] = res.status
            CASE_STATUS[random_key]['run_time'] = response_time
            CASE_STATUS[random_key]['is_fail'] = is_fail
            CASE_STATUS[random_key]['success' if not is_fail else 'fail'] += 1
            CASE_STATUS[random_key]['is_login'] = config['is_login']

            self.api_report['success' if not is_fail else 'fail'] += 1
            self.api_report['run_api'] += 1

            if config['is_login']:
                self.cookies[temp_data[num].host] = await get_cookie(rep_type='aiohttp', response=res)

            # 提取code
            # if config.get('code'):
            #     ocr = ddddocr.DdddOcr(show_ad=False)
            #     self.code = ocr.classification(res.content)
            #
            # # 从html文本中提取数据
            # if config.get('extract'):
            #     _extract = config['extract']
            #     self.extract = await my_extract(
            #         pattern=_extract[0],
            #         string=await res.text(encoding='utf-8'),
            #         index=_extract[1]
            #     )

            # logger.info(f"case_id:{case_id},状态码: {res.status}")

            self.api_report['total_time'] += response_time

            if response_time > self.api_report['max_time']:
                self.api_report['max_time'] = response_time

            try:
                res_json = await res.json(content_type='application/json' if not temp_data[num].file else None)
                res_json = {} if res_json is None else res_json
            except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError):
                res_json = {}

            response.append(res_json)
            response_headers.append(dict(res.headers))

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

            config['sleep'] = 0.3
            await asyncio.sleep(config['sleep'])
            logger.debug(f"case_id:{case_id},响应信息: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
            logger.info(f"{'=' * 30}case_id:{case_id},结束请求,number:{num}{'=' * 30}")

            self.api_report['fail_stop'] = config.get('fail_stop', False)
            self.api_report['initiative_stop'] = config.get('stop', False)

            # 接口测试报告详情数据收集
            CASE_RESPONSE[case_id].append(
                {
                    'path': url,
                    'params': params,
                    'data': request_info['__data'],
                    'headers': dict(res.headers),
                    'response': res_json,
                }
            )

            api_detail['number'] = num
            api_detail['status'] = 'pass' if not is_fail else 'fail'
            api_detail['method'] = temp_data[num].method
            api_detail['host'] = temp_data[num].host
            api_detail['path'] = case_data[num].path
            api_detail['run_time'] = response_time
            api_detail['request_info'] = request_info
            api_detail['response_info'] = {
                'status_code': res.status,
                'response': res_json,
                'response_headers': dict(res.headers)
            }
            api_detail['expect_info'] = check
            api_detail['actual_info'] = actual
            api_detail['jsonpath_info'] = js_count(
                case_id=case_id,
                case_list=[case_data[num]],
                temp_list=[temp_data[num]],
                run_case=CASE_RESPONSE
            )
            api_detail['conf_info'] = config
            api_detail['other_info'] = {
                'description': case_data[num].description if case_data[num].description else '--',
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
                'file': True if temp_data[num].file else False,
                'assert_info': result
            }

            api_detail_list.append(api_detail)
            CASE_STATUS_LIST[random_key].append(copy.deepcopy(CASE_STATUS[random_key]))

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
                del CASE_STATUS[random_key]
                await self.sees.close()
                break

        if CASE_STATUS_LIST.get(random_key):
            CASE_STATUS_LIST[random_key][-1]['run'] = False

        asyncio.create_task(self._del_case_status(random_key))

        case_info = await service_crud.get_case_info(db=db, case_id=case_id)

        # 填充报告列表信息
        self.api_report['case_id'] = case_id
        self.api_report['total_api'] = len(temp_data)
        self.api_report['is_fail'] = all_is_fail
        self.api_report['avg_time'] = self.api_report['total_time'] / self.api_report['run_api']

        # 存入api报告
        await write_api_report(db=db, api_report=self.api_report, api_detail=api_detail_list)

        logger.info(
            f"用例: {temp_pro}-{temp_name}-{case_info[0].case_name} 执行完成, 进行结果校验, 序号: {case_info[0].run_order}")
        await self.sees.close()
        return f"{temp_pro}-{temp_name}-{case_info[0].case_name}", self.api_report

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

    async def _polling(
            self,
            case_id: int,
            sleep: int,
            check: dict,
            request_info: dict,
            files,
            random_key: str,
            db_config: dict
    ):
        """
        轮询执行接口
        :param case_id:
        :param sleep:
        :param check:
        :param request_info:
        :param files:
        :param random_key:
        :param db_config:
        :return:
        """

        # check = copy.deepcopy(check)
        CASE_STATUS[random_key]['request_info'] = request_info
        polling_fail = False  # 标记是否失败
        num = 0
        while True:
            logger.debug(f"循环case_id:{case_id},{num + 1}次: {request_info['url']}")
            if files:
                files_data = FormData()
                for file in files:
                    files_data.add_field(
                        name=file['name'],
                        value=base64.b64decode(file['value'].encode('utf-8')),
                        content_type=file['contentType'],
                        filename=file['fileName'].encode().decode('unicode_escape')
                    )
                request_info['data'] = files_data

            start_time = time.monotonic()
            res = await self.sees.request(**request_info, allow_redirects=False)
            response_time = time.monotonic() - start_time

            if files:
                request_info['data'] = [
                    {
                        'name': file['name'],
                        'content_type': file['contentType'],
                        'filename': file['fileName']

                    } for file in files
                ]

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

                break
            del check['status_code']

            try:
                res_json = await res.json(content_type='application/json' if not files else None)
            except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError) as e:
                logger.debug(f"res.json()错误信息: {str(e)}")
                res_json = {}

            CASE_STATUS[random_key]['response_info'] = res_json

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

                if isinstance(v, (str, int, float, bool, dict)):
                    is_fail = await AssertCase.assert_case(
                        k=k,
                        compare='==',
                        expect=v,
                        actual=value,
                        result=result
                    )
                else:
                    is_fail = await AssertCase.assert_case(
                        k=k,
                        compare=v[0],
                        expect=v[1],
                        actual=value,
                        result=result
                    )

                if is_fail:
                    polling_fail = True

            logger.info(f"第{num + 1}次匹配")
            logger.debug(f"实际-{result}")
            logger.debug(f"预期-{check}")

            if CASE_STATUS[random_key]['stop']:
                asyncio.create_task(self._del_case_status(random_key))
                break

            CASE_STATUS[random_key]['sleep'] = sleep
            CASE_STATUS[random_key]['expect'] = check
            CASE_STATUS[random_key]['actual'] = result

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

        return res, polling_fail, response_time, result

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

    async def _replace_headers(self, tmp_header: dict, case_header: dict, tmp_host: str, tmp_file: bool) -> dict:
        """
        替换headers中的内容
        :param tmp_header:
        :param case_header:
        :return:
        """
        for k, v in case_header.items():
            tmp_header[k] = v

        # 替换cookie
        if self.cookies.get(tmp_host):
            if tmp_header.get('Cookie'):
                tmp_header['Cookie'] = self.cookies[tmp_host]
            if tmp_header.get('cookie'):
                tmp_header['cookie'] = self.cookies[tmp_host]

        # 有附件时，要删除Content-Type
        if tmp_file:
            del tmp_header['Content-Type']

        # aiohttp 需要删除Content-Length
        if tmp_header.get('Content-Length'):
            del tmp_header['Content-Length']

        return tmp_header
