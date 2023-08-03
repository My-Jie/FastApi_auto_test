#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: database.py
@Time: 2022/8/9-21:51
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from tools.read_setting import setting

# 数据库访问地址
DB_URL = setting['sqlite']

# 启动引擎
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    # echo=True
)
# 启动会话
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=True)

# 数据模型的基类
Base = declarative_base()
# Base.metadata.create_all(bind=engine)
