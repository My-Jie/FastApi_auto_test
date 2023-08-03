#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2022/8/9-16:07
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union


class YApi(BaseModel):
    group_id: int
    group_name: str
    group_desc: str
    project_id: int
    project_name: str
    api_count: Optional[int] = 0

    class Config:
        orm_mode = True


class YApiOut(YApi):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class YApiData(BaseModel):
    project_id: int
    api_id: int
    title: str
    path: str
    req_headers: Optional[list] = []
    method: str
    req_params: Optional[list] = []
    json_body: str
    req_data: Union[dict, list]

    class Config:
        orm_mode = True


class YApiDataOut(YApiData):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
