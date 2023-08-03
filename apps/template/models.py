#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/8-10:22
"""

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, JSON
from tools.database import Base


class Template(Base):
    """
    场景模板名称，及关联的用例，测试数据
    """
    __tablename__ = 'case_template'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String, nullable=True, index=True, comment='项目名称')
    temp_name = Column(String, unique=True, nullable=True, index=True, comment='场景名称')
    api_count = Column(Integer, default=0, nullable=True, comment='接口数量')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class TemplateData(Base):
    """
    场景数据列表
    """
    __tablename__ = 'case_template_data'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    temp_id = Column(Integer, ForeignKey('case_template.id'))
    number = Column(Integer, nullable=False, comment='序号')
    host = Column(String, nullable=False, comment='域名')
    path = Column(String, nullable=False, index=True, comment='接口路径')
    code = Column(Integer, nullable=False, comment='响应状态码')
    method = Column(String, nullable=False, comment='请求方法')
    params = Column(JSON, comment='请求参数数据')
    json_body = Column(String, nullable=False, comment='json格式/表单格式')
    data = Column(JSON, comment='json/表单 数据')
    file = Column(Integer, default=0, comment='是否有附件')
    file_data = Column(JSON, comment='文件数据')
    headers = Column(JSON, comment='请求头')
    response = Column(JSON, comment='响应数据')
    description = Column(String, comment='用例描述')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
