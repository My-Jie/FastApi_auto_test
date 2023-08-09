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
from apps.run_case import crud
from apps.run_case import CASE_STATUS
from .check_data import check_customize
from tools import replace_data
from tools.replace_data import COUNT


class RunApi:
    def __init__(self):
        timeout = aiohttp.ClientTimeout(total=120)
        self.sees = aiohttp.client.ClientSession(timeout=timeout)
        self.cookies = {}
        self.code = None  # 存验证码数据
        self.extract = None  # 存提取的内容
        self.fk = FakerData()
        self.case_status = {
            'case_id': 0,
            'total': 0,
            'stop': False,
            'success': 0,
            'fail': 0,
            'sleep': 0,
            'actual': {},
            'expect': {},
            'request_info': {},
            'response_info': {},
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
        CASE_STATUS[random_key] = self.case_status

        temp_data = copy.deepcopy(temp_data)
        case_data = copy.deepcopy(case_data)
        # 返回结果收集
        response = []
        result = []
        is_fail = False
        for num in range(len(temp_data)):
            config: dict = copy.deepcopy(dict(case_data[num].config))
            logger.debug(f"{'=' * 30}case_id:{case_id},开始请求,number:{num}{'=' * 30}")
            try:
                # 识别url表达式
                url = await replace_data.replace_url(
                    db=db,
                    old_str=f"{temp_data[num].host}{case_data[num].path}",
                    response=response,
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
                    faker=self.fk,
                    customize=customize
                )
                # 识别校验的数据
                check = await replace_data.replace_params_data(
                    db=db,
                    data=case_data[num].check,
                    response=response,
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
            response_info = await self._polling(
                case_id=case_id,
                sleep=config['sleep'],
                check=check,
                request_info=request_info,
                files=temp_data[num].file_data,
                random_key=random_key,
                db_config=db_config
            )
            res, is_fail = response_info

            if not is_fail:
                CASE_STATUS[random_key]['success'] += 1
            else:
                CASE_STATUS[random_key]['fail'] += 1

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

            # 收集结果
            request_info['file'] = True if temp_data[num].file else False
            request_info['expect'] = check
            request_info['description'] = case_data[num].description if case_data[num].description else ''
            request_info['config'] = case_data[num].config
            try:
                res_json = await res.json(content_type='application/json' if not temp_data[num].file else None)
                res_json = {} if res_json is None else res_json
            except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError):
                res_json = {}
            request_info['response'] = res_json
            response.append(res_json)

            # 判断响应结果，调整校验内容收集
            if res.status != check['status_code']:
                request_info['actual'] = {'status_code': [res.status]}
            else:
                new_check = copy.deepcopy(check)
                del new_check['status_code']
                request_info['actual'] = {
                    **{'status_code': [res.status]},
                    **{k: jsonpath.jsonpath(res_json, f'$..{k}') for k in new_check if 'sql_' not in k},
                    **{k: [new_check[k][1]] for k in new_check if 'sql_' in k}
                }

            config['sleep'] = 0.3
            await asyncio.sleep(config['sleep'])
            result.append(request_info)
            logger.debug(f"case_id:{case_id},响应信息: {json.dumps(res_json, indent=2, ensure_ascii=False)}")
            logger.info(f"{'=' * 30}case_id:{case_id},结束请求,number:{num}{'=' * 30}")

            # 失败停止的判断
            if setting['global_fail_stop'] and is_fail and config.get('fail_stop'):
                logger.info(f"case_id:{case_id},编号: {num} 校验错误-退出执行")
                await self.sees.close()
                break

            if config.get('stop'):
                logger.info(f"case_id:{case_id},number:{num} 接口配置信息stop = {config['stop']}, 停止后续接口请求")
                await self.sees.close()
                break

            if CASE_STATUS[random_key]['stop']:
                logger.info(f"case_id:{case_id},number:{num} 手动停止执行")
                del CASE_STATUS[random_key]
                await self.sees.close()
                break

        asyncio.create_task(self._del_case_status(random_key))

        case_info = await crud.update_test_case_order(db=db, case_id=case_id, is_fail=is_fail)

        await crud.queue_add(db=db, data={
            'start_time': int(time.time() * 1000),
            'case_name': f'{temp_pro}-{temp_name}-{case_info.case_name}',
            'case_data': result
        })
        logger.info(f"用例: {temp_pro}-{temp_name}-{case_info.case_name} 执行完成, 进行结果校验, 序号: {case_info.run_order}")
        await self.sees.close()
        return f"{temp_pro}-{temp_name}-{case_info.case_name}", \
               case_info.run_order, \
               case_info.success, \
               case_info.fail, \
               is_fail

    @staticmethod
    async def _check_count(check: dict):
        """
        对校验数据进行加减乘除
        :param check:
        :return:
        """
        for k, v in check.items():
            for x in COUNT:
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
        await asyncio.sleep(20)
        if CASE_STATUS.get(random_key):
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
        is_fail = False  # 标记是否失败
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
                        filename=file['fileName']
                    )
                request_info['data'] = files_data

            res = await self.sees.request(**request_info, allow_redirects=False)

            if files:
                request_info['data'] = [
                    {
                        'name': file['name'],
                        'content_type': file['contentType'],
                        'filename': file['fileName']

                    } for file in files
                ]

            status_code = check['status_code']
            if check['status_code'] != res.status:
                is_fail = True
                break
            del check['status_code']

            try:
                res_json = await res.json(content_type='application/json' if not files else None)
            except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError) as e:
                logger.debug(f"res.json()错误信息: {str(e)}")
                res_json = {}

            CASE_STATUS[random_key]['response_info'] = res_json
            result = []
            for k, v in check.items():
                # 从数据库获取需要的值
                if isinstance(v, list) and 'sql_' == k[:4]:
                    sql_data = await self._sql_data(v[1], db_config)
                    if v[0] == sql_data[0]:
                        result.append({k: sql_data[0]})
                    else:
                        is_fail = True
                    check[k][1] = sql_data[0]
                    continue

                # 从响应信息获取需要的值
                value = jsonpath.jsonpath(res_json, f'$..{k}')

                if value:
                    value = value[0]

                if isinstance(v, (str, int, float, bool, dict)):
                    if v == value:
                        result.append({k: value})
                    else:
                        is_fail = True

                elif isinstance(v, list):
                    if v[0] == '<':
                        if value < v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '<=':
                        if value <= v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '==':
                        if value == v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '!=':
                        if value != v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '>=':
                        if value >= v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '>':
                        if value > v[1]:
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == 'in':
                        if value in str(v[1]):
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '!in':
                        if v[1] in str(value):
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == 'not in':
                        if value not in str(v[1]):
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == 'notin':
                        if value not in str(v[1]):
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '!not in':
                        if v[1] not in str(value):
                            result.append({k: value})
                        else:
                            is_fail = True
                    elif v[0] == '!notin':
                        if v[1] not in str(value):
                            result.append({k: value})
                        else:
                            is_fail = True

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
            if len(check) == len(result) + 1:
                is_fail = False
                break

            if sleep < 5:
                break

            await asyncio.sleep(5)
            sleep -= 5
            num += 1

        return res, is_fail

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
