#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/6/9-16:30
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, Text, JSON
from tools.database import Base


class PlaywrightTemp(Base):
    """
    用例名称表
    """
    __tablename__ = 'playwright_temp'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String, nullable=True, index=True, comment='系统名称')
    temp_name = Column(String, nullable=True, index=True, comment='模板名称')
    rows = Column(Integer, default=0, nullable=True, comment='行数')
    run_order = Column(Integer, default=0, nullable=True, comment='执行次数')
    success = Column(Integer, default=0, nullable=True, comment='成功次数')
    fail = Column(Integer, default=0, nullable=True, comment='失败次数')
    text = Column(Text, default=0, nullable=True, comment='py文件内容')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class PlaywrightCaseDate(Base):
    """
    测试数据
    """
    __tablename__ = 'playwright_case_data'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    temp_id = Column(Integer, ForeignKey('playwright_temp.id'))
    case_name = Column(String, nullable=True, index=True, comment='用例名称')
    rows_data = Column(JSON, comment='测试数据')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
