#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/22-9:50
"""

import datetime
from typing import List
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from apps.case_ddt import models, schemas


async def create_test_gather(db: AsyncSession, data: schemas.TestGrater):
    """
    创建模板数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TestGather(**data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def del_test_gather(db: AsyncSession, case_id: int, suite: list = None):
    """
    删除测试数据集
    :param db:
    :param case_id:
    :param suite:
    :return:
    """
    if suite:
        await db.execute(
            delete(
                models.TestGather
            ).filter(
                models.TestGather.case_id == case_id,
                models.TestGather.suite.in_(suite)
            )
        )
        await db.commit()
        return

    await db.execute(
        delete(models.TestGather).filter(models.TestGather.case_id == case_id)
    )
    await db.commit()


async def get_gather(db: AsyncSession, case_id: int, number: int = None, suite: List[int] = None):
    """
    模糊查询url
    :param db:
    :param case_id:
    :param number:
    :param suite:
    :return:
    """
    if suite:
        result = await db.execute(
            select(
                models.TestGather
            ).filter(
                models.TestGather.case_id == case_id,
                models.TestGather.suite.in_(suite)
            ).order_by(
                models.TestGather.suite
            ).order_by(
                models.TestGather.number
            )
        )
        return result.scalars().all()

    result = await db.execute(
        select(
            models.TestGather
        ).filter(
            models.TestGather.case_id == case_id
        ).order_by(
            models.TestGather.suite
        ).order_by(
            models.TestGather.number
        )
    )
    return result.scalars().all()


async def get_all(db: AsyncSession):
    """
    查询全部的数据集
    :param db:
    :return:
    """
    result = await db.execute(
        select(models.TestGather)
    )
    return result.scalars().all()


async def get_count(db: AsyncSession, today: bool = None):
    """
    记数查询
    :param db:
    :param today:
    :return:
    """
    if today:
        result = await db.execute(
            select(
                func.count(models.TestGather.suite.distinct())
            ).filter(
                models.TestGather.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.TestGather.suite.distinct()))
    )
    return result.scalar()
