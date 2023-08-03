#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/22-9:50
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, JSON
from tools.database import Base


class TestGather(Base):
    """
    测试数据集
    """
    __tablename__ = 'test_gather'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('test_case.id'))
    suite = Column(Integer, nullable=False, comment='数据集编号')
    name = Column(String, nullable=True, index=True, comment='数据集名称')
    number = Column(Integer, nullable=False, comment='序号')
    path = Column(String, nullable=False, comment='接口路径')
    params = Column(JSON, comment='请求参数数据集')
    data = Column(JSON, comment='body参数数据集')
    headers = Column(JSON, comment='headers参数数据集')
    check = Column(JSON, comment='校验数据集')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
