#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/4-15:24
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, JSON
from tools.database import Base


class YAoiProject(Base):
    """
    YApi项目表
    """
    __tablename__ = 'yapi_project'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, index=True, comment='项目分组id')
    group_name = Column(String, index=True, comment='项目分组名称')
    group_desc = Column(String, comment='项目分组描述')

    project_id = Column(Integer, index=True, comment='项目id')
    project_name = Column(String, index=True, comment='项目名称')
    api_count = Column(String, default=0, comment='接口数量')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class YApiPool(Base):
    """
    用例池数据
    """
    __tablename__ = 'yapi_pool'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('yapi_project.id'), index=True)
    api_id = Column(Integer, index=True, comment='接口id')
    title = Column(String, comment='接口名称')
    path = Column(String, comment='接口路径')
    req_headers = Column(JSON, comment='请求头')
    method = Column(String, comment='请求方法')
    req_params = Column(JSON, comment='请求参数数据')
    json_body = Column(String, comment='json格式/表单格式')
    req_data = Column(JSON, comment='请求数据')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
