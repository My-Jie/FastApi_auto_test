#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_api.py
@Time: 2022/8/23-15:20
"""

import re
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
from apps.whole_conf import crud as conf_crud
from .check_data import check_customize

COUNT = ['+', '-', '*', '/', '//', '%']


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
                url = await self._replace_url(
                    db=db,
                    old_str=f"{temp_data[num].host}{case_data[num].path}",
                    response=response,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别params表达式
                params = await replace_params_data(
                    db=db,
                    data=case_data[num].params,
                    response=response,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别data表达式
                data = await replace_params_data(
                    db=db,
                    data=case_data[num].data,
                    response=response,
                    faker=self.fk,
                    code=self.code,
                    extract=self.extract,
                    customize=customize
                )
                # 识别headers中的表达式
                case_header = await replace_params_data(
                    db=db,
                    data=case_data[num].headers,
                    response=response,
                    faker=self.fk,
                    customize=customize
                )
                # 识别校验的数据
                check = await replace_params_data(
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

    @staticmethod
    async def _replace_url(
            db: Session,
            old_str: str,
            response: list,
            faker: FakerData,
            code: str,
            extract: str,
            customize: dict
    ) -> str:
        """
        替换url的值
        :param old_str:
        :param response:
        :param faker:
        :param code:
        :param extract:
        :return:
        """
        return await header_srt(
            db=db,
            x=old_str,
            response=response,
            faker=faker,
            value_type='url',
            code=code,
            extract=extract,
            customize=customize
        )

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


async def replace_params_data(
        db: Session,
        data: [dict, list],
        response: list,
        faker: FakerData,
        code: str = None,
        extract: str = '',
        customize: dict = None
) -> dict:
    """
    替换params和data的值
    """

    async def handle_value(data_json):

        if isinstance(data_json, list):
            return [await handle_value(x) for x in data_json]

        if isinstance(data_json, str):
            return await header_srt(
                db=db,
                x=data_json,
                response=response,
                faker=faker,
                code=code,
                extract=extract,
                customize=customize
            )

        target = {}
        if not data_json:
            return target
        for key in data_json.keys():
            if isinstance(data_json[key], str):
                target[key] = await header_srt(
                    db=db,
                    x=data_json[key],
                    response=response,
                    faker=faker,
                    code=code,
                    extract=extract,
                    customize=customize
                )
                continue

            if isinstance(data_json[key], dict):
                target[key] = await handle_value(data_json[key])
                continue

            if isinstance(data_json[key], list):
                new_list = []
                for x in data_json[key]:
                    if isinstance(x, (list, dict)):
                        new_list.append(await handle_value(x))
                    elif isinstance(x, str):
                        new_list.append(await header_srt(
                            db=db,
                            x=x,
                            response=response,
                            faker=faker,
                            code=code,
                            extract=extract,
                            customize=customize
                        ))
                    else:
                        new_list.append(x)

                target[key] = new_list
                continue

            target[key] = data_json[key]

        return target

    return await handle_value(data)


async def header_srt(
        db: Session,
        x: str,
        response: list,
        faker: FakerData,
        value_type: str = None,
        code: str = None,
        extract: str = '',
        customize: dict = None

):
    """
    处理数据
    :param db:
    :param x:
    :param response:
    :param faker:
    :param value_type:
    :param code:
    :param extract:
    :param customize:
    :return:
    """
    # 接口上下级数据关联的参数提取
    if "{{" in x and "$" in x and "}}" in x:
        replace_values: List[str] = re.compile(r'{{(.*?)}}', re.S).findall(x)
        for replace in replace_values:
            new_value = await _header_str_param(x=replace, response=response)

            if value_type == 'url':
                x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
                continue

            if isinstance(new_value, (str, float, int)):
                if isinstance(new_value, (float, int)) and [_ for _ in COUNT if _ in x]:
                    x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
                else:
                    x = re.sub("{{(.*?)}}", str(new_value), x, count=1)
            else:
                x = new_value

    # 自定参数提取
    if "%{{" in x and "}}" in x:
        replace_key: List[str] = re.compile(r'%{{(.*?)}}', re.S).findall(x)
        for key in replace_key:
            value = customize.get(key, '_')
            if value == '_':
                customize_info = await conf_crud.get_customize(
                    db=db,
                    key=key
                )
                value = customize_info[0].value if customize_info else None

            if value_type == 'url':
                x = re.sub("%{{(.*?)}}", str(value), x, count=1)
            else:
                x = re.sub("%{{(.*?)}}", str(value), x, count=1)

    # 假数据提取
    if isinstance(x, str) and "{" in x and "}" in x:
        replace_values: List[str] = re.compile(r'{(.*?)}', re.S).findall(x)
        for replace in replace_values:
            if replace == 'get_code':
                x = code
            elif 'get_extract' in replace:
                x = extract
            else:
                new_value = await _header_str_func(x=replace, faker=faker)
                if new_value is None:
                    return x

                if value_type == 'url':
                    x = re.sub("{(.*?)}", str(new_value), x, count=1)
                    continue

                if len(replace) + 2 == len(x):
                    x = new_value
                else:
                    x = re.sub("{(.*?)}", str(new_value), x, count=1)

    return x


async def _header_str_param(x: str, response: list):
    """
    提取参数：字符串内容
    :param x:
    :param response:
    :return:
    """
    num, json_path = x.split('.', 1)

    # 字符串截取
    start_index, end_index = None, None
    if "|" in json_path:
        json_path, str_index = json_path.split('|', 1)
        start_index, end_index = str_index.split(':', 1)

    if ',' in json_path:
        json_path, seek_list = json_path.split(',', 1)
        extract_key = json_path.split('.')[-1]
        seek_list = seek_list.split(',')

        value = set()
        for seek in seek_list:
            seek_value, compare, seek_name = seek.strip().split(' ')
            # 同级相邻
            value_set = await _header_adjoin(seek_name, seek_value, compare, extract_key, response[int(num)])
            if value_set:
                if not value:
                    value = value_set
                value = value & value_set

        if value:
            return list(value)[0]
        else:
            return ''

    value = jsonpath.jsonpath(response[int(num)], json_path)
    if value:
        if start_index is None and end_index is None:
            return value[0]
        else:
            if isinstance(value[0], str):
                try:
                    return value[0][
                           int(start_index):int(
                               end_index) if end_index != '' else None
                           ]
                except ValueError:
                    return value[0]
            else:
                return value[0]
    else:
        return ''


async def _header_adjoin(seek_name: str, seek_value: str, compare: str, extract_key: str, response_data):
    """

    :param seek_name: 相邻的key
    :param seek_value: 相邻的key的内容
    :param compare: 比较符
    :param extract_key: 需要提取的字段
    :param response_data: 响应内容
    :return:
    """
    path_list = jsonpath.jsonpath(response_data, f'$..{seek_name}', result_type='IPATH')

    if not path_list:
        return []

    value_list = []
    for path in path_list:
        json_data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
        if compare == 'in' and json_data and seek_value in json_data[0]:
            path[-1] = extract_key
            data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
            value_list.append(data[0] if data else None)
            continue

        if compare == '==' and json_data and seek_value == json_data[0]:
            path[-1] = extract_key
            data = jsonpath.jsonpath(response_data, f"$.{'.'.join(path)}")
            value_list.append(data[0] if data else None)
            continue

    return set(value_list)


async def _header_str_func(x: str, faker: FakerData):
    """
    处理随机方法生成的数据
    :param x:
    :param faker:
    :return:
    """
    try:
        if '.' in x:
            func, param = x.split('.', 1)
        else:
            func, param = x, 1

        value = faker.faker_data(func=func, param=param)
        if value is None:
            return None

        return value if value else x

    except ValueError:
        return x
