#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/10/24-21:38
"""

import datetime
from typing import List
from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from apps.api_report import schemas, models


async def create_api_list(db: AsyncSession, data: schemas.ApiReportListInt):
    """
    创建测试报告列表
    :param db:
    :param data:
    :return:
    """
    db_data = models.ApiReportList(**data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def get_max_run_number(db: AsyncSession, case_ids: List[int]):
    """
    获取最大的运行编号
    :param db:
    :param case_ids:
    :return:
    """
    result = await db.execute(
        select(
            models.ApiReportList.case_id, func.max(models.ApiReportList.run_number)
        ).filter(
            models.ApiReportList.case_id.in_(case_ids),
        ).group_by(
            models.ApiReportList.case_id
        )
    )
    return result.all()


async def get_api_list(db: AsyncSession, case_id: int, page: int = 1, size: int = 10):
    """
    获取测试报告列表
    :param db:
    :param case_id:
    :param page:
    :param size:
    :return:
    """
    result = await db.execute(
        select(
            models.ApiReportList
        ).where(
            models.ApiReportList.case_id == case_id
        ).order_by(
            models.ApiReportList.id.desc()
        ).offset(size * (page - 1)).limit(size)
    )
    return result.scalars().all()


async def create_api_detail(db: AsyncSession, data: List[dict], report_id: int):
    """
    创建测试报告详情
    :param db:
    :param data:
    :param report_id:
    :return:
    """
    for x in data:
        d = schemas.ApiReportDetailInt(**x)
        db_data = models.ApiReportDetail(**d.dict(), report_id=report_id)
        db.add(db_data)
    await db.commit()
    # db.refresh(db_data)
    # return db_data


async def get_api_detail(db: AsyncSession, report_id: int, page: int = 1, size: int = 10):
    """
    获取测试报告详情
    :param db:
    :param report_id:
    :param page:
    :param size:
    :return:
    """
    result = await db.execute(
        select(
            models.ApiReportDetail
        ).where(
            models.ApiReportDetail.report_id == report_id
        ).offset(size * (page - 1)).limit(size)
    )
    return result.scalars().all()


async def delete_api_report(db: AsyncSession, report_id: int):
    """
    删除测试用例报告
    :param db:
    :param report_id:
    :return:
    """
    await db.execute(
        delete(models.ApiReportList).filter(models.ApiReportList.id == report_id)
    )
    await db.commit()


async def delete_api_detail(db: AsyncSession, report_id: int):
    """
    删除报告详情
    :param db:
    :param report_id: 
    :return:
    """
    await db.execute(
        delete(models.ApiReportList).filter(models.ApiReportDetail.report_id == report_id)
    )


async def get_report_count(db: AsyncSession, today: bool = False):
    if today:
        result = await db.execute(
            select(
                func.count(models.ApiReportList.id)
            ).filter(
                models.ApiReportList.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.ApiReportList.id))
    )
    return result.scalar()
