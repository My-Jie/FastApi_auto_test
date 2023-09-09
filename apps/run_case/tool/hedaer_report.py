#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: hedaer_report.py
@Time: 2023/9/10-1:56
"""

from sqlalchemy.orm import Session
from tools.load_allure import load_allure_report
from apps.run_case import crud as run_crud
from .run_pytest import allure_generate
from tools.read_setting import setting


async def report(db: Session, report: list):
    for info in report:
        # 数据更新
        case_info = await run_crud.update_test_case_order(db=db, case_id=info['case_id'], is_fail=info['is_fail'])
        info['report'] = f"/allure/{info['case_id']}/{case_info.run_order}"
        info['success'] = case_info.success
        info['fail'] = case_info.fail
        info['run_order'] = case_info.run_order

        # 输出报告
        await allure_generate(
            allure_plus_dir=info['allure_plus_dir'],
            run_order=info['run_order'],
            allure_path=info['allure_path'],
            report_url=setting['host'],
            case_name=info['case_name'],
            case_id=info['case_id'],
        )

        # 加载静态页面
        await load_allure_report(
            allure_dir=info['allure_dir'],
            case_id=info['case_id'],
            run_order=info['run_order']
        )
