#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_ui.py
@Time: 2023/9/3-21:42
"""

import time
from sqlalchemy.orm import Session
from apps.case_ui import crud as ui_crud
from tools.read_setting import setting
from tools.faker_data import FakerData
from tools.load_allure import load_allure_report
from apps.run_case.tool import run


async def run_ui(db: Session, playwright_text: str, temp_id: int):
    """
    生成临时py脚本
    :param db:
    :param playwright_text:
    :param temp_id:
    :return:
    """

    # 写入临时的py文件
    f = FakerData()
    path = f'./files/tmp/{int(time.time() * 1000)}_{f.faker_data("random_lower", 6)}.py'
    with open(path, 'w', encoding='utf-8') as w:
        w.write(playwright_text)

    case_info = await ui_crud.get_playwright(db=db, temp_id=temp_id)

    # 校验结果，生成报告
    allure_dir = setting['allure_path_ui']
    await run(
        test_path=path,
        allure_dir=allure_dir,
        report_url=setting['host'],
        case_name=case_info[0].temp_name,
        case_id=temp_id,
        run_order=case_info[0].run_order + 1,
        ui=True
    )

    case_info = await ui_crud.update_ui_temp_order(db=db, temp_id=temp_id, is_fail=False)
    await load_allure_report(allure_dir=allure_dir, case_id=temp_id, run_order=case_info.run_order, ui=True)

    return {
        'temp_id': case_info.id,
        'report': f'/ui/allure/{case_info.id}/{case_info.run_order}',
        'is_fail': True,
        'run_order': case_info.run_order,
        'success': case_info.success,
        'fail': case_info.fail,
        'tmp_file': path
    }
