#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2022/8/9-16:03
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Union


# 模板名称的请求/响应数据模型
class TemplateIn(BaseModel):
    temp_name: str
    project_name: str = None

    class Config:
        orm_mode = True


class TemplateOut(TemplateIn):
    id: int = None
    api_count: int = None
    created_at: datetime = None
    updated_at: datetime = None

    class Config:
        orm_mode = True


class TestCase(BaseModel):
    id: int
    mode: str = None
    name: str
    run_num: int = None

    class Config:
        orm_mode = True


class TempTestCase(TemplateOut):
    case_count: int = None
    case_info: List[TestCase]

    class Config:
        orm_mode = True


# 测试模板数据的请求/响应数据模型
class TemplateDataIn(BaseModel):
    number: Union[int, str]
    host: HttpUrl
    path: str
    code: int
    method: str
    params: Optional[dict] = {}
    json_body: str
    data: Union[dict, list] = {}
    file: bool
    file_data: Optional[list] = []
    headers: Optional[dict] = {}
    response: Union[dict, list, str] = None
    description: Union[str, None] = None

    class Config:
        orm_mode = True


class TemplateDataInTwo(TemplateDataIn):
    temp_id: int


class TemplateDataOut(TemplateDataIn):
    id: int
    temp_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TempChangeParams(BaseModel):
    temp_id: int
    temp_name: str
    number: int
    path: str
    params: dict
    data: dict


class SwapDataOne(BaseModel):
    temp_id: int
    old_number: int
    new_number: int


class SwapDataMany(BaseModel):
    temp_id: int
    new_numbers: List[int]


class UpdateName(BaseModel):
    new_name: str
    temp_id: int = None


class PaginationTempTestCase(BaseModel):
    total: int
    page: int
    size: int
    items: List[TempTestCase]
