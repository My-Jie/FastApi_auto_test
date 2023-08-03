#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/23-13:45
"""

import re
import os
import time
import random
import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from depends import get_db
from starlette.background import BackgroundTask
from apps import response_code
from apps.template import crud
from apps.case_service import crud as case_crud
from apps.case_ddt import crud as gather_crud
from apps.case_ui import crud as ui_crud
from apps.run_case import schemas, CASE_STATUS, SETTING_INFO_DICT
from apps.setting_bind import crud as setting_crud
from apps.whole_conf import crud as conf_crud
from .tool import run_service_case, run_ddt_case, run_ui_case, header, replace_playwright, check_customize
from tools.read_setting import setting

run_case = APIRouter()

# 临时的环境列表缓存
SETTING_LIST = {}


@run_case.post(
    '/case',
    response_class=response_code.MyJSONResponse,
    name='按用例Id执行',
    description='按用例ID的顺序执行'
)
async def run_case_name(ids: schemas.RunCase, db: Session = Depends(get_db)):
    if not ids.case_ids:
        return await response_code.resp_400()

    if SETTING_LIST.get(ids.setting_list_id):
        del SETTING_LIST[ids.setting_list_id]

    report = await run_service_case(
        db=db,
        case_ids=ids.case_ids,
        setting_info_dict=SETTING_INFO_DICT.get(ids.setting_list_id, {})
    )

    if SETTING_INFO_DICT.get(ids.setting_list_id):
        del SETTING_INFO_DICT[ids.setting_list_id]

    return await response_code.resp_200(data={'allure_report': report})


@run_case.post(
    '/temp',
    response_class=response_code.MyJSONResponse,
    name='按模板Id执行',
    description='按模板ID查询出关联的用例，再异步执行所有用例，收集结果集'
)
async def run_case_name(temp_ids: List[int], db: Session = Depends(get_db)):
    case_list = [await case_crud.get_case_ids(db=db, temp_id=x) for x in temp_ids]

    all_case_list = []
    temp_info = {}
    for x in range(len(case_list)):
        temp_info[temp_ids[x]] = [i[0] for i in case_list[x]]
        for y in case_list[x]:
            all_case_list.append(y[0])

    if not all_case_list:
        return await response_code.resp_404()

    # 按模板并发
    tasks = [asyncio.create_task(run_service_case(db=db, case_ids=[case_id])) for case_id in all_case_list]
    result = await asyncio.gather(*tasks)

    new_result = {}
    for x in result:
        new_result.update(x)
    return await response_code.resp_200(data={'allure_report': new_result, "temp_info": temp_info})


@run_case.post(
    '/gather',
    name='选择数据集执行用例',
    response_class=response_code.MyJSONResponse,
)
async def run_case_gather(rcs: schemas.RunCaseGather, db: Session = Depends(get_db)):
    """
    按数据集执行用例
    """
    gather_data = await gather_crud.get_gather(db=db, case_id=rcs.case_id, suite=rcs.suite)
    if not gather_data:
        return await response_code.resp_404()

    if SETTING_LIST.get(rcs.setting_list_id):
        del SETTING_LIST[rcs.setting_list_id]

    # 获取用例数据,按数据集分套替换数据
    case_data = await case_crud.get_case_data(db=db, case_id=rcs.case_id)
    new_case_data = await header(case_data=case_data, gather_data=gather_data)

    # 运行用例
    if rcs.async_:
        tasks = [
            asyncio.create_task(
                run_ddt_case(
                    db=db,
                    case_id=rcs.case_id,
                    case_info=[data],
                    setting_info_dict=SETTING_INFO_DICT.get(rcs.setting_list_id, {})
                )
            ) for data in new_case_data
        ]
        result = await asyncio.gather(*tasks)

        new_result = {}
        for x in result:
            new_result.update(x)

        if SETTING_INFO_DICT.get(rcs.setting_list_id):
            del SETTING_INFO_DICT[rcs.setting_list_id]

        return await response_code.resp_200(data={'allure_report': new_result})
    else:
        report = await run_ddt_case(
            db=db,
            case_id=rcs.case_id,
            case_info=new_case_data,
            setting_info_dict=SETTING_INFO_DICT.get(rcs.setting_list_id, {})
        )

        if SETTING_INFO_DICT.get(rcs.setting_list_id):
            del SETTING_INFO_DICT[rcs.setting_list_id]

        return await response_code.resp_200(data={'allure_report': report})


@run_case.post(
    '/ui/temp',
    name='执行ui脚本用例',
)
async def ui_temp(rut: schemas.RunUiTemp, db: Session = Depends(get_db)):
    """
    执行ui脚本用例
    """
    ui_temp_info = await ui_crud.get_playwright(db=db, temp_id=rut.temp_id)
    if ui_temp_info:
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
            return await response_code.resp_400(message='由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败')

        report = await run_ui_case(db=db, playwright_text=playwright, temp_id=rut.temp_id)
        report['video'] = f"http://{setting['selenoid']['selenoid_ui_host']}/video/{file_name}.mp4"
        return await response_code.resp_200(
            data=report,
            background=BackgroundTask(lambda: os.remove(report['tmp_file']))
        )
    else:
        return await response_code.resp_404()


@run_case.get(
    '/case/status',
    name='获取用例运行的状态',
    response_class=response_code.MyJSONResponse,
)
async def case_status(key_id: str = None):
    if key_id:
        if CASE_STATUS.get(key_id):
            CASE_STATUS[key_id]['stop'] = True
            return await response_code.resp_200(message='停止成功')
        else:
            return await response_code.resp_200(message='没有运行这个用例')
    return CASE_STATUS


@run_case.get(
    '/get/api/setting/info',
    name='获取api用例绑定的环境配置信息'
)
async def get_api_setting_info(case_id: int, db: Session = Depends(get_db)):
    """
    获取api用例绑定的环境配置信息
    """
    case_info = await case_crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return response_code.resp_404()

    # 获取模板中的原始host
    hosts = await crud.get_temp_host(db=db, temp_id=case_info[0].temp_id)
    hosts = list(set(hosts))

    # 获取环境配置信息，并把配置信息处理成dict
    setting_info = await setting_crud.get_setting(db=db)

    setting_list = []
    setting_list_id = f"{int(time.time() * 1000)}_{random.uniform(0, 1)}"
    num = 1
    for setting_ in setting_info:

        if case_id in setting_.api_case_ids:
            setting_dict = {
                'setting_name': setting_.name,
                'case_id': case_id,
                'setting_list_id': setting_list_id,
                'id_card': f"{int(time.time() * 1000)}_{random.uniform(0, 1)}",
                'virtual_id': num,
                'temp_host': [{'name': '', 'host': x.host, 'change': False} for x in hosts],
                'host': [],
                'customize': [],
                'db': []
            }

            # 查询并处理host
            for x in await conf_crud.get_host(db=db, ids=setting_.host_ids):
                setting_dict['host'].append(
                    {
                        'name': x.name,
                        'host': x.host,
                        'change': True
                    }
                )

            # 查询并处理customize
            for x in await conf_crud.get_customize(db=db, ids=setting_.customize_ids):
                setting_dict['customize'].append(
                    {
                        'name': x.name,
                        'key': x.key,
                        'type': x.type,
                        'value': x.value,
                        'change': True
                    }
                )

            # 查询并处理db
            for x in await conf_crud.get_db(db=db, ids=setting_.db_ids):
                setting_dict['db'].append(
                    {
                        'name': x.name,
                        'host': x.host,
                        'user': x.user,
                        'password': x.password,
                        'database': x.database,
                        'port': x.port,
                        'charset': x.charset,
                        'change': True
                    }
                )

            num += 1
            setting_list.append(setting_dict)

        SETTING_LIST[setting_list_id] = setting_list

    return setting_list


@run_case.get(
    '/get/ui/setting/info',
    name='获取ui用例绑定的环境配置信息'
)
async def get_ui_setting_info(case_id: int, db: Session = Depends(get_db)):
    """
    获取ui用例绑定的环境配置信息
    """
    case_info = await ui_crud.get_playwright(db=db, temp_id=case_id)
    if not case_info:
        return response_code.resp_404()

    # 获取环境配置信息，并把配置信息处理成dict
    setting_info = await setting_crud.get_setting(db=db)

    setting_list = []
    setting_list_id = f"{int(time.time() * 1000)}_{random.uniform(0, 1)}"
    num = 1
    for setting_ in setting_info:

        if case_id in setting_.api_case_ids:
            setting_dict = {
                'setting_name': setting_.name,
                'case_id': case_id,
                'setting_list_id': setting_list_id,
                'id_card': f"{int(time.time() * 1000)}_{random.uniform(0, 1)}",
                'virtual_id': num,
                'customize': [],
            }

            # 查询并处理customize
            for x in await conf_crud.get_customize(db=db, ids=setting_.customize_ids):
                setting_dict['customize'].append(
                    {
                        'name': x.name,
                        'key': x.key,
                        'type': x.type,
                        'value': x.value,
                        'change': True
                    }
                )

            num += 1
            setting_list.append(setting_dict)

        SETTING_LIST[setting_list_id] = setting_list

    return setting_list


@run_case.put(
    '/set/api/setting/info',
    name='设置api用例环境信息'
)
async def set_api_setting_info(
        setting_list_id: str = '',
        id_card: str = '',
        conf_type: str = '',
        temp_host: list = None,
        customize: list = None,
        db_: list = None,
):
    if not conf_type:
        return

    if not SETTING_LIST.get(setting_list_id):
        return await response_code.resp_404(message='没有这个环境数据缓存')

    for x in SETTING_LIST[setting_list_id]:
        if x['id_card'] == id_card:
            if conf_type == 'host':
                x['temp_host'] = temp_host

            if conf_type == 'customize':
                x['customize'] = customize

            if conf_type == 'db':
                x['db'] = db_

            SETTING_INFO_DICT[setting_list_id] = x

            break
    else:
        return await response_code.resp_404(message='没有这个环境数据缓存选项')

    return await response_code.resp_200()
