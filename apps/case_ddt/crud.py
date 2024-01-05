#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/22-9:50
"""

import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from apps.case_ddt import models, schemas


async def create_test_gather(db: Session, data: schemas.TestGrater):
    """
    创建模板数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TestGather(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def del_test_gather(db: Session, case_id: int, suite: list = None):
    """
    删除测试数据集
    :param db:
    :param case_id:
    :param suite:
    :return:
    """
    if suite:
        db.query(models.TestGather).filter(
            models.TestGather.case_id == case_id,
            models.TestGather.suite.in_(suite)
        ).delete()
        db.commit()
        return

    db.query(models.TestGather).filter(models.TestGather.case_id == case_id).delete()
    db.commit()


async def get_gather(db: Session, case_id: int, number: int = None, suite: List[int] = None):
    """
    模糊查询url
    :param db:
    :param case_id:
    :param number:
    :param suite:
    :return:
    """
    if suite:
        return db.query(models.TestGather).filter(
            models.TestGather.case_id == case_id,
            models.TestGather.suite.in_(suite)
        ).order_by(
            models.TestGather.suite
        ).order_by(
            models.TestGather.number
        ).all()

    return db.query(models.TestGather).filter(models.TestGather.case_id == case_id).order_by(
        models.TestGather.suite
    ).order_by(
        models.TestGather.number
    ).all()


async def get_all(db: Session):
    """
    查询全部的数据集
    :param db:
    :return:
    """
    return db.query(models.TestGather).all()


async def get_count(db: Session, today: bool = None):
    """
    记数查询
    :param db:
    :param today:
    :return:
    """
    if today:
        return db.query(func.count(models.TestGather.suite.distinct())).filter(
            models.TestGather.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.TestGather.suite.distinct())).scalar()
