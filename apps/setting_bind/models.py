#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/7/27-16:05
"""

from sqlalchemy import Column, Integer, JSON, DateTime, String, func
from tools.database import Base


class SettingSet(Base):
    """
    环境列表
    """
    __tablename__ = 'setting_set'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    host_ids = Column(JSON, comment='域名id列表')
    customize_ids = Column(JSON, comment='自定参数id列表')
    db_ids = Column(JSON, comment='数据库id列表')
    api_case_ids = Column(JSON, index=True, comment='api用例id列表')
    ui_case_ids = Column(JSON, index=True, comment='api用例id列表')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
