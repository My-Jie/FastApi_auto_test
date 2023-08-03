#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: insert_case_data.py
@Time: 2022/8/21-21:54
"""

from sqlalchemy.orm import Session
from apps.case_service import schemas, crud


async def cover_insert(db: Session, case_id: int, case_data: dict):
    """
    覆盖数据写入
    :param db:
    :param case_id,:
    :param case_data:
    :return:
    """
    # 删除数据，不删除用例名称
    await crud.del_test_case_data(db=db, case_id=case_id)

    case_count = 0
    for data in case_data['data']:
        data['number'] = case_count
        if case_count == 0:
            data['headers'] = {}
        await crud.create_test_case_data(db=db, data=schemas.TestCaseDataIn(**data), case_id=case_id)
        case_count += 1

    return await crud.update_test_case(db=db, case_id=case_id, case_count=case_count)


async def insert(db: Session, case_name: str, temp_id: int, case_data: dict):
    """
    新建测试数据
    :param db:
    :param case_name:
    :param case_data:
    :return:
    """
    db_case = await crud.create_test_case(db=db, case_name=case_name, mode=case_data['mode'], temp_id=temp_id)
    case_count = 0
    for data in case_data['data']:
        data['number'] = case_count
        if case_count == 0:
            data['headers'] = {}
        await crud.create_test_case_data(db=db, data=schemas.TestCaseDataIn(**data), case_id=db_case.id)
        case_count += 1

    return await crud.update_test_case(db=db, case_id=db_case.id, case_count=case_count)
