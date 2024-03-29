#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/10/24-21:38
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, JSON
from apps.base_model import Base


class ApiReportList(Base):
    """
    接口测试报告列表
    """
    __tablename__ = 'api_report_list'

    case_id: Mapped[int] = mapped_column(Integer, ForeignKey('test_case.id'), index=True, comment='用例id')
    run_number: Mapped[int] = mapped_column(Integer, nullable=False, comment='运行编号')
    total_api: Mapped[int] = mapped_column(Integer, comment='总接口数')
    initiative_stop: Mapped[int] = mapped_column(Integer, comment='主动停止')
    fail_stop: Mapped[int] = mapped_column(Integer, comment='失败停止')
    result: Mapped[dict] = mapped_column(JSON, comment='结果')
    time: Mapped[dict] = mapped_column(JSON, comment='耗时')


class ApiReportDetail(Base):
    """
    接口测试报告详情
    """
    __tablename__ = 'api_report_detail'

    report_id: Mapped[int] = mapped_column(Integer, ForeignKey('api_report_list.id'), index=True, comment='报告id')
    api_info: Mapped[dict] = mapped_column(JSON, comment='接口信息')
    history: Mapped[dict] = mapped_column(JSON, comment='历史模板数据')
    request_info: Mapped[dict] = mapped_column(JSON, comment='请求信息')
    response_info: Mapped[list] = mapped_column(JSON, comment='响应信息')
    assert_info: Mapped[list] = mapped_column(JSON, comment='断言信息')
    report: Mapped[dict] = mapped_column(JSON, comment='结果信息')
    config: Mapped[dict] = mapped_column(JSON, comment='配置信息')
    check: Mapped[dict] = mapped_column(JSON, comment='预期校验信息')
    jsonpath_info: Mapped[list] = mapped_column(JSON, comment='jsonpath信息')
    other_info: Mapped[dict] = mapped_column(JSON, comment='其他信息')
