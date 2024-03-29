#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/22-9:50
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, JSON
from apps.base_model import Base


class TestGather(Base):
    """
    测试数据集
    """
    __tablename__ = 'test_gather'

    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('test_case.id'), index=True, comment='用例id')
    suite: Mapped[int] = mapped_column(Integer, nullable=False, comment='数据集编号')
    name: Mapped[str] = mapped_column(String, nullable=True, index=True, comment='数据集名称')
    number: Mapped[int] = mapped_column(Integer, nullable=False, comment='序号')
    path: Mapped[str] = mapped_column(String, nullable=False, comment='接口路径')
    params: Mapped[dict] = mapped_column(JSON, comment='请求参数数据集')
    data: Mapped[dict] = mapped_column(JSON, comment='body参数数据集')
    headers: Mapped[dict] = mapped_column(JSON, comment='headers参数数据集')
    check: Mapped[dict] = mapped_column(JSON, comment='校验数据集')
