#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/6/9-16:30
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, Text, JSON
from apps.base_model import Base


class PlaywrightTemp(Base):
    """
    用例名称表
    """
    __tablename__ = 'playwright_temp'

    # project_name = Column(Integer, nullable=True, index=True, comment='系统名称')
    sys_name: Mapped[int] = mapped_column(Integer, nullable=True, index=True, comment='系统名称')
    temp_name: Mapped[str] = mapped_column(String, nullable=True, index=True, comment='模板名称')
    rows: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='行数')
    run_order: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='执行次数')
    success: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='成功次数')
    fail: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='失败次数')
    text: Mapped[str] = mapped_column(Text, default=0, nullable=True, comment='py文件内容')


class PlaywrightCaseDate(Base):
    """
    测试数据
    """
    __tablename__ = 'playwright_case_data'

    temp_id: Mapped[int] = mapped_column(Integer, ForeignKey('playwright_temp.id'), index=True, comment='模板id')
    case_name: Mapped[str] = mapped_column(String, nullable=True, index=True, comment='用例名称')
    rows_data: Mapped[dict] = mapped_column(JSON, comment='测试数据')
