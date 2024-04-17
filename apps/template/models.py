#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/8-10:22
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, JSON
from apps.base_model import Base


class Template(Base):
    """
    场景模板名称，及关联的用例，测试数据
    """
    __tablename__ = 'case_template'

    project_name: Mapped[int] = mapped_column(Integer, nullable=True, index=True, comment='系统名称')
    temp_name: Mapped[str] = mapped_column(String, unique=True, nullable=True, index=True, comment='场景名称')
    api_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='接口数量')


class TemplateData(Base):
    """
    场景数据列表
    """
    __tablename__ = 'case_template_data'

    temp_id: Mapped[int] = mapped_column(Integer, ForeignKey('case_template.id'), index=True, comment='模板id')
    number: Mapped[int] = mapped_column(Integer, nullable=False, comment='序号')
    host: Mapped[str] = mapped_column(String, nullable=False, comment='域名')
    path: Mapped[str] = mapped_column(String, nullable=False, index=True, comment='接口路径')
    code: Mapped[int] = mapped_column(Integer, nullable=False, comment='响应状态码')
    method: Mapped[str] = mapped_column(String, nullable=False, comment='请求方法')
    json_body: Mapped[str] = mapped_column(String, nullable=False, comment='json格式/表单格式')
    params: Mapped[dict] = mapped_column(JSON, comment='请求参数数据')
    data: Mapped[dict] = mapped_column(JSON, comment='json/表单 数据')
    file: Mapped[int] = mapped_column(Integer, default=0, comment='是否有附件')
    file_data: Mapped[dict] = mapped_column(JSON, comment='文件数据')
    headers: Mapped[dict] = mapped_column(JSON, comment='请求头')
    response: Mapped[dict] = mapped_column(JSON, comment='响应数据')
    response_headers: Mapped[dict] = mapped_column(JSON, comment='响应请求头')
    description: Mapped[str] = mapped_column(String, comment='用例描述')
