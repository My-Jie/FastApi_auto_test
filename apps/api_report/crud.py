#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/10/24-21:38
"""

import datetime
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from apps.api_report import schemas, models


async def create_api_list(db: Session, data: schemas.ApiReportListInt):
    """
    创建测试报告列表
    :param db:
    :param data:
    :return:
    """
    db_data = models.ApiReportList(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def get_max_run_number(db: Session, case_ids: List[int]):
    """
    获取最大的运行编号
    :param db:
    :param case_ids:
    :return:
    """
    return db.query(func.max(models.ApiReportList.run_number)).filter(
        models.ApiReportList.case_id.in_(case_ids),
    ).group_by(
        models.ApiReportList.case_id
    ).all()


async def get_api_list(db: Session, case_id: int, page: int = 1, size: int = 10):
    """
    获取测试报告列表
    :param db:
    :param case_id:
    :param page:
    :param size:
    :return:
    """
    return db.query(models.ApiReportList).filter(
        models.ApiReportList.case_id == case_id,
    ).order_by(
        models.ApiReportList.id.desc()
    ).offset(size * (page - 1)).limit(size).all()


async def create_api_detail(db: Session, data: List[dict], report_id: int):
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
    db.commit()
    # db.refresh(db_data)
    # return db_data


async def get_api_detail(db: Session, report_id: int, page: int = 1, size: int = 10):
    """
    获取测试报告详情
    :param db:
    :param report_id:
    :param page:
    :param size:
    :return:
    """
    return db.query(models.ApiReportDetail).filter(
        models.ApiReportDetail.report_id == report_id
    ).offset(size * (page - 1)).limit(size).all()


async def delete_api_report(db: Session, report_id: int):
    """
    删除测试用例报告
    :param db:
    :param report_id:
    :return:
    """
    db.query(models.ApiReportList).filter(
        models.ApiReportList.id == report_id
    ).delete()


async def delete_api_detail(db: Session, report_id: int):
    """
    删除报告详情
    :param db:
    :param report_id: 
    :return:
    """
    db.query(models.ApiReportDetail).filter(
        models.ApiReportDetail.report_id == report_id
    ).delete()


async def get_report_count(db: Session, today: bool = False):
    if today:
        return db.query(func.count(models.ApiReportList.id)).filter(
            models.ApiReportList.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.ApiReportList.id)).scalar()
