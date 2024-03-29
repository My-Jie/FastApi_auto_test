#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2022/8/20-21:59
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, JSON
from apps.base_model import Base


class TestCase(Base):
    """
    用例名称表
    """
    __tablename__ = 'test_case'

    temp_id: Mapped[int] = mapped_column(Integer, ForeignKey('case_template.id'), index=True, comment='模板id')
    case_name: Mapped[str] = mapped_column(String, nullable=True, index=True, comment='用例名称')
    case_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='用例数量')
    mode: Mapped[str] = mapped_column(String, comment='用例运行模式')
    run_order: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='执行次数')
    success: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='成功次数')
    fail: Mapped[int] = mapped_column(Integer, default=0, nullable=True, comment='失败次数')


class TestCaseData(Base):
    """
    用例数据表
    """
    __tablename__ = 'test_case_data'

    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('test_case.id'), index=True, comment='用例id')
    number: Mapped[int] = mapped_column(Integer, nullable=False, comment='序号')
    path: Mapped[str] = mapped_column(String, nullable=False, comment='接口路径')
    headers: Mapped[dict] = mapped_column(JSON, comment='请求头测试数据')
    params: Mapped[dict] = mapped_column(JSON, comment='请求参数测试数据')
    data: Mapped[dict] = mapped_column(JSON, comment='json/表单 测试数据')
    file: Mapped[int] = mapped_column(Integer, comment='是否有附件')
    check: Mapped[dict] = mapped_column(JSON, comment='测试数据校验字段')
    description: Mapped[str] = mapped_column(String, comment='用例描述')
    config: Mapped[dict] = mapped_column(JSON, comment='用例配置')
