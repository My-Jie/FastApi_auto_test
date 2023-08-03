#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: db.py
@Time: 2022/8/11-16:36
"""

from tools.database import SessionLocal


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
