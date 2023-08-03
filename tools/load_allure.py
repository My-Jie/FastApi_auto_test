#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: load_allure.py
@Time: 2022/9/3-22:55
"""

import os
from .global_log import logger
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI


def load_allure_reports(app: FastAPI, allure_dir: str, ui: bool = False):
    """
    加载所有的allures测试报告
    :param app:
    :param allure_dir: 测试报告目录
    :param ui
    :return:
    """
    try:
        files = os.listdir(os.path.join(allure_dir))
    except FileNotFoundError:
        return
    for case_id in files:
        try:
            run_orders = os.listdir(os.path.join(allure_dir, case_id, 'allure_plus'))
        except FileNotFoundError:
            return
        for run_order in run_orders:
            if run_order == 'history.json':
                continue
            if ui:
                allure_url = f"/ui/allure/{case_id}/{run_order}"
            else:
                allure_url = f"/allure/{case_id}/{run_order}"
            allure_path = f'{allure_dir}/{case_id}/allure_plus/{run_order}'
            app.mount(allure_url, StaticFiles(directory=allure_path, html=True))
            logger.debug(f"加载allure静态报告, url:{allure_url}, path:{allure_path}")


async def load_allure_report(allure_dir: str, case_id: int, run_order: int, ui: bool = False):
    """
    加载单个allure测试报告
    :param allure_dir: 测试报告目录
    :param case_id: 测试用例id
    :param run_order: 测试用例执行序号
    :param ui:
    :return:
    """
    from main import app
    if ui:
        allure_url = f"/ui/allure/{case_id}/{run_order}"
    else:
        allure_url = f"/allure/{case_id}/{run_order}"
    allure_path = f'{allure_dir}/{case_id}/allure_plus/{run_order}'
    app.mount(allure_url, StaticFiles(directory=allure_path, html=True))
    logger.debug(f"加载allure静态报告, url:{allure_url}, path:{allure_path}")
