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


class ApiReportListInt(BaseModel):
    case_id: int
    is_fail: bool
    run_number: int
    run_api: int
    total_api: int
    initiative_stop: int
    fail_stop: int
    success: int
    fail: int
    total_time: Union[float, int]
    max_time: Union[float, int]
    avg_time: Union[float, int]

    class Config:
        orm_mode = True


class ApiReportListOut(ApiReportListInt):
    id: int
    created_at: datetime
    updated_at: datetime


class ApiReportDetailInt(BaseModel):
    status: str
    number: int
    method: str
    host: str
    path: str
    run_time: Union[float, int]
    request_info: Optional[dict] = {}
    response_info: Optional[dict] = {}
    expect_info: Optional[dict] = {}
    actual_info: Optional[dict] = {}
    jsonpath_info: Union[list, dict] = []
    conf_info: Optional[dict] = {}
    other_info: Optional[dict] = {}

    class Config:
        orm_mode = True


class ApiReportDetailOut(ApiReportDetailInt):
    id: int
    report_id: int

    created_at: datetime
    updated_at: datetime
