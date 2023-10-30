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
    is_fail = Column(Integer, comment='执行结果')
    run_number = Column(Integer, nullable=False, comment='运行编号')
    run_api = Column(Integer, comment='执行接口')
    total_api = Column(Integer, comment='总接口')
    initiative_stop = Column(Integer, comment='主动停止')
    fail_stop = Column(Integer, comment='失败停止')
    success = Column(Integer, comment='成功条数')
    fail = Column(Integer, comment='失败条数')
    total_time = Column(Integer, comment='总耗时')
    max_time = Column(Integer, comment='最大耗时')
    avg_time = Column(Integer, comment='平均耗时')

    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class ApiReportDetail(Base):
    """
    接口测试报告详情
    """
    __tablename__ = 'api_report_detail'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey('api_report_list.id'), index=True)
    number = Column(Integer, comment='运行序号')
    status = Column(String, comment='结果')
    method = Column(String, comment='请求方法')
    host = Column(String, comment='主机地址')
    path = Column(String, comment='请求路径')
    run_time = Column(Integer, comment='耗时')
    request_info = Column(JSON, comment='请求信息')
    response_info = Column(JSON, comment='响应信息')
    expect_info = Column(JSON, comment='预期信息')
    actual_info = Column(JSON, comment='实际信息')
    jsonpath_info = Column(JSON, comment='jsonpath信息')
    conf_info = Column(JSON, comment='配置信息')
    other_info = Column(JSON, comment='其他信息')

    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
