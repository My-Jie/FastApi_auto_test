#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2023/4/16-14:42
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Union, Any
from enum import Enum


class ModeEnum(str, Enum):
    string = 'string'
    int = 'int'
    float = 'float'
    number = 'number'
    list = 'list'
    dict = 'dict'
    boolean = 'boolean'
    null = 'null'


class ConfHostIn(BaseModel):
    name: str
    host: HttpUrl


class ConfHostOut(ConfHostIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfProjectIn(BaseModel):
    name: str
    code: str


class ConfProjectOut(ConfProjectIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfDBIn(BaseModel):
    name: str = '测试数据库'
    host: str = '127.0.0.1'
    user: str = 'read'
    password: str = '123456'
    database: str = 'test'
    port: str = '3306'
    charset: str = 'utf-8'


class ConfDBOut(ConfDBIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfUnifyResIn(BaseModel):
    name: str
    key: str
    type: ModeEnum
    value: Union[int, str, None]


class ConfUnifyResOut(ConfUnifyResIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ConfCustomizeIn(BaseModel):
    name: str
    key: str
    type: ModeEnum
    value: Union[Any, None]


class ConfCustomizeOut(ConfCustomizeIn):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
