#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2022/8/20-22:00
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Union
from enum import Enum


class ModeEnum(str, Enum):
    service = 'service'
    ddt = 'ddt'
    perf = 'perf'


class KeyValueType(str, Enum):
    key = 'key'
    value = 'value'


class RepType(str, Enum):
    params = 'params'
    data = 'data'
    headers = 'headers'
    response = 'response'
    response_headers = 'response_headers'


class ExtType(str, Enum):
    equal = '=='
    contain = 'in'


class SetApiDescription(BaseModel):
    case_id: int
    number: int
    description: str = None


class CheckInfo(BaseModel):
    key: str
    s: str
    type: str
    value: Union[float, int, str, bool, None]


class SetApiCheck(BaseModel):
    case_id: int
    number: int
    type: str
    check: CheckInfo


class HeaderInfo(BaseModel):
    key: str
    value: str


class setApiHeader(BaseModel):
    case_id: int
    number: int
    type: str
    header: HeaderInfo


class SedParamsData(BaseModel):
    case_id: int
    number: int
    type: str
    data_info: Union[dict, list]


# 用例名称的请求/响应数据模型
class TestCaseIn(BaseModel):
    case_name: str
    mode: ModeEnum

    class Config:
        orm_mode = True


class TestCaseOut(TestCaseIn):
    id: int
    temp_id: int
    case_count: int
    run_order: int
    success: int
    fail: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# 测试用例的数据模型
class TestCaseConfig(BaseModel):
    is_login: bool = None
    sleep: float = 0.3
    stop: bool = None
    code: bool = None
    extract: Union[list, None] = []
    fail_stop: bool = None


class TestCaseDataIn(BaseModel):
    number: Union[str, int]
    path: str
    headers: Optional[dict] = {}
    params: Optional[dict] = {}
    data: Union[dict, list] = {}
    file: bool
    check: Optional[dict] = {}
    description: Union[str, None] = None
    config: TestCaseConfig

    class Config:
        orm_mode = True


class TestCaseDataInTwo(TestCaseDataIn):
    case_id: int


class TestCaseData(BaseModel):
    number: Union[int, str]
    path: str
    headers: Optional[dict] = {}
    params: Optional[dict] = {}
    data: Union[dict, list] = {}
    file: bool
    check: Optional[dict] = {}
    description: Union[str, None] = None
    config: TestCaseConfig

    class Config:
        orm_mode = True


class TestCaseDataOut(BaseModel):
    tips: dict
    temp_name: str = None
    case_name: str = None
    mode: ModeEnum
    data: List[TestCaseData]

    class Config:
        orm_mode = True


class TestCaseDataOut1(BaseModel):
    number: int
    case_id: int
    path: str
    headers: Optional[dict] = {}
    params: Optional[dict] = {}
    data: Union[dict, list] = {}
    file: bool
    check: Optional[dict] = {}
    description: Union[str, None] = None
    config: TestCaseConfig

    class Config:
        orm_mode = True


class TestCaseDataOut2(TestCaseDataOut1):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TestCaseInfoOut(BaseModel):
    name: str
    case_name: str
    temp_name: str
    case_id: int
    api_count: int = None
    run_order: int = None
    success: int = None
    fail: int = None
    mode: str = None
    report: datetime = None
    created_at: datetime = None
    updated_at: datetime = None


class SwapOne(BaseModel):
    case_id: int
    old_number: int
    new_number: int


class SwapMany(BaseModel):
    case_id: int
    new_numbers: List[int]


class SetApiConfig(BaseModel):
    case_id: int
    number: int
    config: TestCaseConfig


class UpdateName(BaseModel):
    new_name: str
    case_id: int = None


class PaginationTestCaseInfo(BaseModel):
    total: int
    page: int
    size: int
    items: List[TestCaseInfoOut]
