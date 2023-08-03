#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2023/7/27-16:04
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Union, List


class SettingSetIn(BaseModel):
    name: str
    host_ids: Union[List[int]] = []
    customize_ids: Union[List[int]] = []
    db_ids: Union[List[int]] = []
    api_case_ids: Union[List[int]] = []
    ui_case_ids: Union[List[int]] = []


class SettingSetOut(SettingSetIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
