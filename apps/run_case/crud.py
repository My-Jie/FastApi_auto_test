#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/23-13:56
"""

from sqlalchemy.orm import Session
from apps.run_case import models as queue
from apps.case_service import models as service_case


async def queue_add(db: Session, data: dict):
    """
    添加消息列队
    :param db:
    :param data:
    :return:
    """
    db_data = queue.RunCaseQueue(**data)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def queue_query(db: Session):
    """
    查询
    :param db:
    :return:
    """
    return db.query(queue.RunCaseQueue).order_by(queue.RunCaseQueue.start_time).all()


async def queue_del(db: Session, queue_id: int = None):
    """
    删除输出
    :param db:
    :param queue_id:
    :return:
    """
    if queue_id is not None:
        db.query(queue.RunCaseQueue).filter(queue.RunCaseQueue.id == queue_id).delete()
        db.commit()
        return

    db.query(queue.RunCaseQueue).delete()


async def update_test_case_order(db: Session, case_id: int, is_fail: bool):
    """
    更新用例次数
    :param db:
    :param case_id:
    :param is_fail: 是否失败
    :return:
    """
    db_case = db.query(service_case.TestCase).filter(service_case.TestCase.id == case_id).first()
    db_case.run_order = db_case.run_order + 1
    if is_fail:
        db_case.fail = db_case.fail + 1
    else:
        db_case.success = db_case.success + 1

    db.commit()
    db.refresh(db_case)
    return db_case
