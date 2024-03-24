#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2023/10/24-21:38
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Union, Optional


class ReportResult(BaseModel):
    run_api: int
    success: int
    fail: int
    skip: int
    result: int


class ReportTime(BaseModel):
    total_time: Union[float, int]
    max_time: Union[float, int]
    avg_time: Union[float, int]


class ApiReportListInt(BaseModel):
    case_id: int
    run_number: int
    total_api: int
    initiative_stop: int
    fail_stop: int
    result: ReportResult
    time: ReportTime

    class Config:
        orm_mode = True


class ApiReportListOut(ApiReportListInt):
    id: int
    created_at: datetime
    updated_at: datetime


class ApiReportDetailInt(BaseModel):
    api_info: Optional[dict] = {}
    history: Optional[dict] = {}
    request_info: Optional[dict] = {}
    response_info: Optional[list] = []
    assert_info: Optional[list] = []
    report: Optional[dict] = {}
    config: Optional[dict] = {}
    check: Optional[dict] = {}
    jsonpath_info: Union[list, dict] = []
    other_info: Optional[dict] = {}

    class Config:
        orm_mode = True


class ApiReportDetailOut(ApiReportDetailInt):
    id: int
    report_id: int

    created_at: datetime
    updated_at: datetime
