#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: write_report.py
@Time: 2023/10/25-11:36
"""

from sqlalchemy.orm import Session
from apps.api_report import schemas, crud
from apps.run_case import crud as run_crud


async def write_api_report(db: Session, api_report: dict, api_detail: list):
    """
    写入数据到测试报告中
    :param db:
    :param api_report:
    :param api_detail:
    :return:
    """
    # 查询最大的run_number
    run_number = await crud.get_max_run_number(db=db, case_id=api_report['case_id'])
    # 写入报告列表
    api_report['run_number'] = run_number + 1 if run_number is not None else 1
    db_data = await crud.create_api_list(db=db, data=schemas.ApiReportListInt(**api_report))
    # 写入详情列表
    await crud.create_api_detail(db=db, data=api_detail, report_id=db_data.id)
    # 更新用例次数
    db_info = await run_crud.update_test_case_order(db=db, case_id=api_report['case_id'], is_fail=api_report['is_fail'])
    api_report['run_order'] = db_info.run_order
    api_report['success_case'] = db_info.success
    api_report['fail_case'] = db_info.fail
