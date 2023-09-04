#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: run_case.py
@Time: 2022/9/28-17:15
"""

import re
import time
import copy
from aiohttp.client_exceptions import (
    ServerTimeoutError,
    ServerConnectionError,
    ServerDisconnectedError,
    ClientConnectorError,
    ClientOSError
)
from typing import List
from sqlalchemy.orm import Session
from apps.case_service import crud as case_crud
from apps.template import crud as temp_crud
from apps.whole_conf import crud as conf_crud
from apps.case_ui import crud as ui_crud
from apps.run_case.tool import RunApi, run
from tools.load_allure import load_allure_report
from tools.read_setting import setting
from apps.run_case.tool.header_host import whole_host
from apps.run_case.tool.run_ui import run_ui
from apps.run_case import SETTING_INFO_DICT, schemas
from .check_data import check_customize
from .header_playwright import replace_playwright


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
                case, run_order, success, fail, is_fail, total_time = await RunApi().fo_service(
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
                'total_time': total_time
            }
        else:
            report[case_id] = {
                'report': f'用例{case_id}不存在',
                'is_fail': True,
                'run_order': 0,
                'success': 0,
                'fail': 0,
                'total_time': 0
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
            case, run_order, success, fail, is_fail, total_time = await RunApi().fo_service(
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
            'total_time': total_time
        }

    return report


async def run_ui_case(db: Session, rut: schemas.RunUiTemp, ui_temp_info: list):
    file_name = f"temp_id_{ui_temp_info[0].id}_{time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))}"

    # 从环境配置里面取数据
    setting_info_dict = SETTING_INFO_DICT.get(rut.setting_list_id, {})
    customize = await check_customize(setting_info_dict.get('customize', {}))

    # 自定参数提取
    temp_text = ui_temp_info[0].text
    replace_key: List[str] = re.compile(r'%{{(.*?)}}', re.S).findall(temp_text)
    for key in replace_key:
        value = customize.get(key, '_')
        if value == '_':
            customize_info = await conf_crud.get_customize(
                db=db,
                key=key
            )
            value = customize_info[0].value if customize_info else None

        temp_text = re.sub("%{{(.*?)}}", str(value), temp_text, count=1)

    if rut.gather_id:
        case_info = await ui_crud.get_play_case_data(db=db, case_id=rut.gather_id, temp_id=rut.temp_id)

        # 替换测试数据
        temp_text = temp_text.split('\n')
        for x in case_info[0].rows_data:
            temp_text[x['row'] - 1] = re.sub(r'{{(.*?)}}', x['data'], temp_text[x['row'] - 1], 1)

        playwright = await replace_playwright(
            playwright_text='\n'.join(temp_text),
            temp_name=ui_temp_info[0].temp_name,
            remote=rut.remote,
            remote_id=rut.remote_id,
            headless=rut.headless,
            file_name=file_name
        )
    else:
        playwright = await replace_playwright(
            playwright_text=temp_text,
            temp_name=ui_temp_info[0].temp_name,
            remote=rut.remote,
            remote_id=rut.remote_id,
            headless=rut.headless,
            file_name=file_name
        )

    if not playwright:
        raise Exception('由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败')

    report = await run_ui(db=db, playwright_text=playwright, temp_id=rut.temp_id)
    report['video'] = f"http://{setting['selenoid']['selenoid_ui_host']}/video/{file_name}.mp4"

    return report
