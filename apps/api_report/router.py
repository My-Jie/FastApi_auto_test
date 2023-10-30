#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/10/24-21:38
"""

from typing import List
from fastapi import APIRouter, Depends
from depends import get_db
from sqlalchemy.orm import Session
from apps import response_code

from apps.api_report import schemas, crud

api_report = APIRouter()


@api_report.get(
    '/list/{case_id}',
    name='查看用例的报告列表',
    response_model=List[schemas.ApiReportListOut]
)
async def report_list(
        case_id: int,
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
):
    return await crud.get_api_list(db=db, case_id=case_id, page=page, size=size)


@api_report.get(
    '/detail/{report_id}',
    name='查看用例的报告详情'
)
async def report_detail(
        report_id: int,
        page: int = 1,
        size: int = 10,
        db: Session = Depends(get_db)
):
    return await crud.get_api_detail(db=db, report_id=report_id, page=page, size=size)
