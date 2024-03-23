#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：executor_service.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/3/22 11:26 
"""

import copy
import time
import json
import base64
import asyncio
import aiohttp
import jsonpath
from aiohttp import FormData
from sqlalchemy.orm import Session
from apps.case_service import crud as case_crud
from apps.template import crud as temp_crud
from aiohttp import client_exceptions

from tools import logger, get_cookie, AsyncMySql
from tools.read_setting import setting

from .base_abstract import ApiBase
from ..handle_headers import replace_headers
from ..run_api_data_processing import DataProcessing
from ..check_data import check_customize
from ..assert_case import AssertCase


class ExecutorService(ApiBase):

    def __init__(self, db: Session):
        super(ExecutorService, self).__init__()
        self._db = db
        self._case_group = {}
        self._setting_info_dict = {}
        self._cookie = {}

    async def collect_sql(self, **kwargs):
        """
        将需要用到的数据，一次性查询出来
        :return:
        """
        # 查询用例数据
        case_data = await case_crud.get_case_data_group(self._db, case_ids=kwargs['case_ids'])
        case_ids = {x[0].id for x in case_data}
        if len(case_ids) != len(kwargs['case_ids']):
            raise ValueError(
                f"不存在的用例: {list(set(kwargs['case_ids']) - case_ids)}"
            )
        temp_data = await temp_crud.get_temp_data_group(
            db=self._db,
            temp_ids=list(set([x[0].temp_id for x in case_data]))
        )

        # 按用例id进行分组
        case_group = {}
        for case in case_data:
            if case[0].id not in case_group:
                case_group[case[0].id] = [list(case)]
            else:
                case_group[case[0].id].append(list(case))

        # 模板加入到用例的分组
        temp_data_dict = {(x[1].temp_id, x[1].number): x for x in temp_data}
        for k, v in case_group.items():
            num = 0
            for v_ in v:
                case_group[k][num] += list(temp_data_dict[(v_[0].temp_id, v_[1].number)])
                num += 1

        # 按用户请求顺序排序
        # {case_id： [(用例，用例详情，模板，模板详情)]}
        self._case_group = {k: case_group[k] for k in kwargs['case_ids']}

    async def collect_config(self, setting_info_dict):
        """
        拿临时的执行配置信息
        :return:
        """
        self._setting_info_dict = setting_info_dict

    async def collect_req_data(self):
        """
        收集请求数据
        :return:
        """
        api_group = []
        for case_id, case_data in self._case_group.items():
            api_list = []
            for case in case_data:
                api_data = {
                    'api_info': {
                        'host': case[3].host,
                        'case_id': case[1].case_id,
                        'number': case[1].number,
                        'temp_name': case[2].temp_name,
                        'case_name': case[0].case_name,
                        'description': case[1].description,
                        'json_body': 'json' if case[3].json_body == 'json' else 'data',
                        'file': case[3].file,
                        'result': 0,  # 成功0、失败1、跳过2
                        'run_status': True  # 执行中ture， 停止false
                    },
                    'history': {
                        'path': case[3].path,
                        'params': case[3].params,
                        'data': case[3].data,
                        'headers': case[3].headers,
                        'response': case[3].response,
                        'response_headers': case[3].response_headers
                    },
                    'request_info': {
                        'url': f'{case[3].host}{case[1].path}',
                        'method': case[3].method,
                        'headers': replace_headers(  # 将用例中的headers临时替换到模板中
                            cookies=self._cookie,
                            tmp_header=case[3].headers,
                            case_header=case[1].headers,
                            tmp_host=case[3].host,
                            tmp_file=case[3].file
                        ),
                        'params': case[1].params,
                        f"{'json' if case[3].json_body == 'json' else 'data'}": case[1].data,
                    },
                    'response_info': [],  # 可能会存在单接口多次请求的情况
                    'report': [],  # 校验结果同理
                    'config': case[1].config,
                    'check': case[1].check,

                }

                # 处理附件上传
                if case[3].file_data:
                    files_data = FormData()
                    for file in case[3].file_data:
                        files_data.add_field(
                            name=file['name'],
                            value=base64.b64decode(file['value'].encode('utf-8')),
                            content_type=file['contentType'],
                            filename=file['fileName'].encode().decode('unicode_escape')
                        )
                    api_data['request_info']['data'] = files_data

                api_list.append(api_data)

            api_group.append(api_list)

        self.api_group = api_group

    async def executor_api(self, sync: bool = True):
        """
        按同步或异步执行用例
        :return:
        """
        if sync:
            for api_list in self.api_group:
                await self._run_api(api_list=api_list)
        else:
            pass

    async def collect_report(self):
        """

        :return:
        """

    async def _run_api(self, api_list: list):
        """
        执行用例
        :param api_list:
        :return:
        """
        sees = aiohttp.client.ClientSession(timeout=aiohttp.ClientTimeout(total=120))

        data_processing = DataProcessing(db=self._db)
        logger.info(
            f"{'=' * 30}{api_list[0]['api_info']['temp_name']}-{api_list[0]['api_info']['case_name']}{'=' * 30}"
        )
        for api in api_list:
            # 处理请求相关的jsonpath数据
            (
                api['request_info']['url'],
                api['request_info']['params'],
                api['request_info'][api['api_info']['json_body']],
                api['request_info']['headers'],
                api['check']
            ) = await data_processing.processing(
                url=api['request_info']['url'],
                params=api['request_info']['params'],
                data=api['request_info'].get('data') or api['request_info'].get('json'),
                headers=api['request_info']['headers'],
                check=api['check'],
                api_list=api_list,
                customize=await check_customize(self._setting_info_dict.get('customize', {})),
            )

            # ⬜️================== 🍉轮询发起请求，单接口的默认间隔时间超过5s，每次请求间隔5s进行轮询🍉 ==================⬜️ #
            sleep = api['config']['sleep']
            while True:
                logger.info(f"{'%-20s' % api['api_info']['description']}-{api['request_info']['url']}")
                start_time = time.monotonic()
                res = await sees.request(**api['request_info'], allow_redirects=False)

                # 循环请求中的信息收集
                response_info = {
                    'status_code': res.status,
                    'response_time': time.monotonic() - start_time,
                    'response': {},
                    'headers': dict(res.headers),
                }
                try:
                    response_info['response'] = await res.json(
                        content_type='application/json' if not api['api_info']['file'] else None
                    ) or {}
                except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError):
                    response_info['response'] = {}
                api['response_info'].append(response_info)

                # 断言结果
                response_info['response']['status_code'] = res.status
                await self._assert(check=api['check'], response=response_info['response'])
                del response_info['response']['status_code']

                # 单接口轮询控制
                if sleep < 5:
                    break
                else:
                    sleep -= 5
                    await asyncio.sleep(5)
            # ⬜️================== 🍉轮询结束请求，单接口的默认间隔时间超过5s，每次请求间隔5s进行轮询🍉 ==================⬜️ #

            # 记录cookie
            if api['config'].get('is_login'):
                self._cookie[api['api_info']['host']] = await get_cookie(rep_type='aiohttp', response=res)

            # 退出循环执行的判断
            if any([
                api['config'].get('stop'),
                setting['global_fail_stop'] and api['config'].get('fail_stop')
            ]):
                await sees.close()
                break

            if api['config'].get('sleep') < 5:
                await asyncio.sleep(api['config']['sleep'])  # 业务场景用例执行下，默认的间隔时间

        await sees.close()

    async def _assert(self, check: dict, response: dict):
        """
        校验结果
        :param check:
        :param response:
        :return:
        """
        for k, v in check.items():
            # 从数据库获取需要的值
            if isinstance(v, list) and 'sql_' == k[:4]:
                sql_data = await self._sql_data(v[1], self._setting_info_dict.get('db', {}))
                is_fail = await AssertCase.assert_case(
                    compare='==',
                    expect=v[0],
                    actual=sql_data[0],
                )

                check[k][1] = sql_data[0]
                continue

            # 从响应信息获取需要的值
            value = jsonpath.jsonpath(response, f'$..{k}')
            if value:
                value = value[0]
            # 校验结果
            is_fail = await AssertCase.assert_case(
                compare='==' if isinstance(v, (str, int, float, bool, dict)) else v[0],
                expect=v if isinstance(v, (str, int, float, bool, dict)) else v[1],
                actual=value,
            )

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
