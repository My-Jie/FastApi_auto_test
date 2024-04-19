#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: db.py
@Time: 2022/8/11-16:36
"""

from tools.database import async_session_local
from sqlalchemy.exc import SQLAlchemyError


async def get_db():
    async with async_session_local() as db:
        yield db
