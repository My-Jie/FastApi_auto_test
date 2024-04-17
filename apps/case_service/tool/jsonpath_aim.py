#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：jsonpath_aim.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/12/29 14:11 
"""

from sqlalchemy.ext.asyncio import AsyncSession
from apps.case_service import crud


async def aim(db: AsyncSession, case_id: int, json_str: dict):
    json_list = []
    if json_str['path']:
        json_list += await __to_json(
            await crud.get_case_info_to_number(db, case_id, json_str['path']),
            'path',
            json_list
        )
    if json_str['params']:
        json_list += await __to_json(
            await crud.get_case_info_to_number(db, case_id, json_str['params']),
            'params',
            json_list
        )
    if json_str['data']:
        json_list += await __to_json(
            await crud.get_case_info_to_number(db, case_id, json_str['data']),
            'data',
            json_list
        )
    if json_str['headers']:
        json_list += await __to_json(
            await crud.get_case_info_to_number(db, case_id, json_str['headers']),
            'headers',
            json_list
        )
    if json_str['check']:
        json_list += await __to_json(
            await crud.get_case_info_to_number(db, case_id, json_str['check']),
            'check',
            json_list
        )

    json_list.sort(key=lambda x: x['number'])
    return json_list


async def __to_json(case_list: list, type_: str, old_list: list):
    """
    提取有用字段，处理成字典
    :param case_list:
    :param type_:
    :param old_list:
    :return:
    """
    json_list = []
    for case in case_list:
        for i in old_list:
            if case.number == i['number']:
                i['type'].append(type_)
                break
        else:
            json_list.append(
                {
                    'id': case.id,
                    'case_id': case.case_id,
                    'number': case.number,
                    'path': case.path,
                    'params': case.params,
                    'data': case.data,
                    'headers': case.headers,
                    'check': case.check,
                    'description': case.description,
                    'type': [type_]
                }
            )

    return json_list
