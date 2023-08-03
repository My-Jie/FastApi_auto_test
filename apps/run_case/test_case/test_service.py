#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: test_service.py
@Time: 2022/8/23-21:29
"""

import asyncio
import allure
import pytest
import typing
from sqlalchemy.orm import sessionmaker
from tools.database import engine
from apps.run_case import crud


async def get_case_info():
    # 建立数据库连接
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)
    session = session_local()

    # 获取数据
    queue_info = await crud.queue_query(db=session)

    # 删除数据
    await crud.queue_del(db=session, queue_id=queue_info[0].id)
    return queue_info[0].case_name, queue_info[0].case_data


loop = asyncio.get_event_loop()
case_name, case_data = loop.run_until_complete(get_case_info())

data_list = [
    [
        x,
        case_data[x]['url'],
        case_data[x]['method'],
        case_data[x]['params'],
        case_data[x].get('data') or case_data[x].get('json'),
        case_data[x]['expect'],
        case_data[x]['actual'],
        case_data[x]['response'],
        case_data[x]['description'],
        case_data[x]['config'],
        case_data[x]['headers'],

    ] for x in range(len(case_data))
]


class TestService:

    @pytest.mark.asyncio
    @allure.feature(case_name)
    @pytest.mark.parametrize(
        'num,url,method,params,data,expect,actual,response,description,config,headers', data_list
    )
    async def test_service(
            self,
            num: int,
            url: str,
            method: str,
            params: dict,
            data: dict,
            expect: dict,
            actual: dict,
            response: dict,
            description: str,
            config: dict,
            headers: dict
    ):

        allure.dynamic.title(f"{description}\n/{url.split('/', 3)[3]}")

        for k, v in expect.items():
            if isinstance(v, list) and 'sql_' == k[:4]:
                await self.assert_value(k, v[0], actual_value={k: [v[1]]})
            else:
                await self.assert_value(k, v, actual_value=actual)

    @staticmethod
    async def assert_value(k: str, v: typing.Any, actual_value: dict):
        """
        校验内容
        :return:
        """
        value = actual_value[k][0] if actual_value[k] else actual_value[k]

        allure.attach(f"期望: {v}，实际: {value}", f'校验内容: {k}')
        if isinstance(v, (str, int, float, bool, dict)):
            assert v == value

        if isinstance(v, list):
            if v[0] == '<':
                assert value < v[1]
            elif v[0] == '<=':
                assert value <= v[1]
            elif v[0] == '==':
                assert value == v[1]
            elif v[0] == '!=':
                assert value != v[1]
            elif v[0] == '>=':
                assert value >= v[1]
            elif v[0] == '>':
                assert value > v[1]
            elif v[0] == 'in':
                assert value in str(v[1])
            elif v[0] == '!in':
                assert v[1] in str(value)
            elif v[0] == 'not in':
                assert value not in str(v[1])
            elif v[0] == 'notin':
                assert value not in str(v[1])
            elif v[0] == '!not in':
                assert v[1] not in str(value)
            elif v[0] == '!notin':
                assert v[1] not in str(value)
            else:
                assert 1 == 0, '未匹配到比较符'
