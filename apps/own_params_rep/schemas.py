#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: schemas.py
@Time: 2023/2/25-21:07
"""

from pydantic import BaseModel, Field
from typing import Optional


class UrlEdit(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_url: bool
    old_url: str = Field(..., min_length=5)
    new_url: str = Field(..., min_length=5)


class ParamsAdd(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_params_add: bool
    key: str = Field(..., min_length=1)
    value: Optional[str] = None


class ParamsEdit(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_params_edit: bool
    old_key: str = Field(..., min_length=1)
    new_key: str = Field(..., min_length=1)
    value: Optional[str] = None


class ParamsDel(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_params_del: bool
    key: str = Field(..., min_length=1)


class DataAdd(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_data_add: bool
    key: str = Field(..., min_length=1)
    value: Optional[str] = None


class DataEdit(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_data_edit: bool
    old_key: str = Field(..., min_length=1)
    new_key: str = Field(..., min_length=1)
    value: Optional[str] = None


class DataDel(BaseModel):
    temp_id: Optional[int] = None
    case_id: Optional[int] = None
    number: int
    rep_data_del: bool
    key: str = Field(..., min_length=1)
