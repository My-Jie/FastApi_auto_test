#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/10/24-21:38
"""

from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, JSON
from tools.database import Base


class ApiReportList(Base):
    """
    接口测试报告列表
    """
    __tablename__ = 'api_report_list'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey('test_case.id'), index=True)
    run_number = Column(Integer, nullable=False, comment='运行编号')
    total_api = Column(Integer, comment='总接口')
    initiative_stop = Column(Integer, comment='主动停止')
    fail_stop = Column(Integer, comment='失败停止')
    result = Column(JSON, comment='结果')
    time = Column(JSON, comment='耗时')

    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class ApiReportDetail(Base):
    """
    接口测试报告详情
    """
    __tablename__ = 'api_report_detail'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey('api_report_list.id'), index=True)
    api_info = Column(JSON, comment='接口信息')
    history = Column(JSON, comment='历史模板数据')
    request_info = Column(JSON, comment='请求信息')
    response_info = Column(JSON, comment='响应信息')
    assert_info = Column(JSON, comment='断言信息')
    report = Column(JSON, comment='结果信息')
    config = Column(JSON, comment='配置信息')
    check = Column(JSON, comment='预期校验信息')
    jsonpath_info = Column(JSON, comment='jsonpath信息')
    other_info = Column(JSON, comment='其他信息')

    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
