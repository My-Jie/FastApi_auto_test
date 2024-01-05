#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2022/8/23-13:56
"""

from typing import List, Optional, Union
from pydantic import BaseModel, HttpUrl


class TempHosts(BaseModel):
    name: str
    host: HttpUrl
    settingHost: Union[None, HttpUrl]
    change: bool

    class Config:
        orm_mode = True


class RunCase(BaseModel):
    case_ids: List[int]
    setting_list_id: str = ''


class RunTemp(BaseModel):
    temp_ids: List[int]


class RunCaseGather(BaseModel):
    case_id: int
    suite: List[int]
    async_: Optional[bool] = False
    setting_list_id: str = ''


class RunUiTemp(BaseModel):
    temp_id: int
    remote: bool
    remote_id: int = None
    headless: bool
    gather_id: int = None
    setting_list_id: str = ''


class RunUiTempGather(RunUiTemp):
    gather_ids: List[int] = None
    async_: Optional[bool] = False
