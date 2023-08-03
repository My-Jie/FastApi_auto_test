#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_case.py
@Time: 2022/9/28-17:15
"""

import time
import copy
from aiohttp.client_exceptions import (
    ServerTimeoutError,
    ServerConnectionError,
    ServerDisconnectedError,
    ClientConnectorError,
    ClientOSError
)
from sqlalchemy.orm import Session
from apps.case_service import crud as case_crud
from apps.template import crud as temp_crud
from apps.case_ui import crud as ui_crud
from apps.run_case.tool import RunApi, run
from tools.load_allure import load_allure_report
from tools.faker_data import FakerData
from tools.read_setting import setting
from apps.run_case.tool.header_host import whole_host


async def run_service_case(db: Session, case_ids: list, setting_info_dict: dict = None):
    """
    执行业务流程用例
    :param db:
    :param case_ids:
    :param setting_info_dict：
    :return:
    """
    report = {}
    for case_id in case_ids:
        case_info = await case_crud.get_case_info(db=db, case_id=case_id)
        if case_info:
            # 拿到测试数据
            case_data = await case_crud.get_case_data(db=db, case_id=case_info[0].id)
            # 拿到模板数据
            temp_data = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)

            if setting_info_dict:
                temp_data = await whole_host(
                    temp_data=copy.deepcopy(temp_data),
                    temp_hosts=setting_info_dict.get('temp_host')
                )

            # 拿到项目名称、模板名称
            temp_info = await temp_crud.get_temp_name(db=db, temp_id=case_info[0].temp_id)
            # 处理数据，执行用例
            try:
                case, run_order, success, fail, is_fail = await RunApi().fo_service(
                    db=db,
                    case_id=case_id,
                    temp_data=temp_data,
                    case_data=case_data,
                    temp_pro=temp_info[0].project_name,
                    temp_name=temp_info[0].temp_name,
                    setting_info_dict=setting_info_dict
                )
            except (
                    ServerTimeoutError,
                    ServerConnectionError,
                    ServerDisconnectedError,
                    ClientConnectorError,
                    ClientOSError
            ) as e:
                raise Exception(f'网络访问失败: {str(e)}')

            except IndexError as e:
                raise Exception(f': {str(e)}')

            # 校验结果，生成报告
            allure_dir = setting['allure_path']
            await run(
                test_path='./apps/run_case/test_case/test_service.py',
                allure_dir=allure_dir,
                report_url=setting['host'],
                case_name=case,
                case_id=case_id,
                run_order=run_order
            )
            await load_allure_report(allure_dir=allure_dir, case_id=case_id, run_order=run_order)

            # report[case_id] = f'{HOST}allure/{case_id}/{run_order}'
            report[case_id] = {
                'report': f'/allure/{case_id}/{run_order}',
                'is_fail': is_fail,
                'run_order': run_order,
                'success': success,
                'fail': fail
            }
        else:
            report[case_id] = {
                'report': f'用例{case_id}不存在',
                'is_fail': True,
                'run_order': 0,
                'success': 0,
                'fail': 0
            }

    return report


async def run_ddt_case(db: Session, case_id: int, case_info: list, setting_info_dict: dict = None):
    """
    执行数据驱动用例
    :param db:
    :param case_id:
    :param case_info:
    :param setting_info_dict:
    :return:
    """
    report = {}
    for case_data in case_info:
        case_info = await case_crud.get_case_info(db=db, case_id=case_id)
        # 拿到模板数据
        temp_data = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)

        if setting_info_dict:
            temp_data = await whole_host(
                temp_data=copy.deepcopy(temp_data),
                temp_hosts=setting_info_dict.get('temp_host')
            )

        # 拿到项目名称、模板名称
        temp_info = await temp_crud.get_temp_name(db=db, temp_id=case_info[0].temp_id)
        # 处理数据，执行用例
        try:
            case, run_order, success, fail, is_fail = await RunApi().fo_service(
                db=db,
                case_id=case_id,
                temp_data=temp_data,
                case_data=case_data,
                temp_pro=temp_info[0].project_name,
                temp_name=temp_info[0].temp_name,
                setting_info_dict=setting_info_dict
            )
        except (
                ServerTimeoutError,
                ServerConnectionError,
                ServerDisconnectedError,
                ClientConnectorError,
                ClientOSError
        ) as e:
            raise Exception(f'网络访问失败: {str(e)}')

        except IndexError as e:
            raise Exception(f': {str(e)}')

        # 校验结果，生成报告
        allure_dir = setting['allure_path']
        await run(
            test_path='./apps/run_case/test_case/test_service.py',
            allure_dir=allure_dir,
            report_url=setting['host'],
            case_name=case,
            case_id=case_id,
            run_order=run_order
        )
        await load_allure_report(allure_dir=allure_dir, case_id=case_id, run_order=run_order)

        # report[case_id] = f'{HOST}allure/{case_id}/{run_order}'
        report[case_id] = {
            'report': f'/allure/{case_id}/{run_order}',
            'is_fail': is_fail,
            'run_order': run_order,
            'success': success,
            'fail': fail,
        }

    return report


async def run_ui_case(db: Session, playwright_text: str, temp_id: int):
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
