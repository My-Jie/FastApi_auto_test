#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: auto_check.py
@Time: 2023/6/23-21:59
"""

from sqlalchemy.orm import Session
from apps.whole_conf import crud as conf_crud


async def my_auto_check(db: Session) -> dict:
    conf = await conf_crud.get_unify_res(db=db)
    auto_check = {}
    for x in conf:
        try:
            if x.type == 'string':
                auto_check[x.key] = str(x.value)
            if x.type == 'number':
                auto_check[x.key] = int(x.value)
            if x.type == 'int':
                auto_check[x.key] = int(x.value)
            if x.type == 'float':
                auto_check[x.key] = float(x.value)
            if x.type == 'boolean':
                auto_check[x.key] = x.value
            if x.type == 'null':
                auto_check[x.key] = None
        except ValueError:
            auto_check[x.key] = x.value

    return auto_check
