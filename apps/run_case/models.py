#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/26-21:53
"""

from sqlalchemy import Column, Integer, JSON, String
from tools.database import Base


class RunCaseQueue(Base):
    """
    消息列队
    """
    __tablename__ = 'run_case_queue'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    start_time = Column(Integer, default=0, nullable=True, comment='记录时间戳')
    case_name = Column(String, comment='用例名称')
    case_data = Column(JSON, comment='测试结果数据')
