#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2022/8/22-9:51
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TestGrater(BaseModel):
    case_id: int
    suite: int
    name: str
    number: int
    path: str
    params: Optional[dict] = {}
    data: Optional[dict] = {}
    check: Optional[dict] = {}
    headers: Optional[dict] = {}

    class Config:
        orm_mode = True


class TestGraterOut(TestGrater):
    id: int
    created_at: datetime
    updated_at: datetime
