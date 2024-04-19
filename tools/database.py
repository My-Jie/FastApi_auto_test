#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: database.py
@Time: 2022/8/9-21:51
"""

from tools.read_setting import setting
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# 引擎
async_engine = create_async_engine(
    url=setting['sqlite'],
    connect_args={"check_same_thread": False},
    # echo=True
)
# 会话
async_session_local = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
