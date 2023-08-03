#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/7/27-15:58
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from apps.setting_bind import crud, schemas
from apps import response_code
from depends import get_db
from .tool import check_setting

# 导入其他模块的crud
from apps.template import crud as temp_crud
from apps.case_service import crud as api_crud
from apps.case_ui import crud as ui_crud
from apps.whole_conf import crud as conf_crud

setting_ = APIRouter()

"""
环境列表的接口
"""


@setting_.post(
    '/add/setting',
    name='添加环境数据',
    response_model=schemas.SettingSetOut
)
async def add_setting(setting: schemas.SettingSetIn, db: Session = Depends(get_db)):
    if await crud.get_setting(db=db, name=setting.name):
        return await response_code.resp_400(message='存在相同的name')

    return await crud.create_setting(db=db, setting=setting)


@setting_.get(
    '/get/setting',
    name='获取环境数据',
    response_model=List[schemas.SettingSetOut]
)
async def get_setting(setting_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_setting(db=db, id_=setting_id)


@setting_.put(
    '/update/name',
    name='修改环境名称',
    response_model=schemas.SettingSetOut
)
async def update_setting(setting_id: int, name: str, db: Session = Depends(get_db)):
    if not await crud.get_setting(db=db, id_=setting_id):
        return await response_code.resp_404()

    return await crud.update_setting_name(db=db, id_=setting_id, name=name)


@setting_.put(
    '/update/bind',
    name='修改环境绑定数据',
    response_model=schemas.SettingSetOut
)
async def update_setting(
        setting_id: int,
        bind: bool,
        api_case: int = None,
        ui_case: int = None,
        host: int = None,
        customize: int = None,
        db_: int = None,
        db: Session = Depends(get_db)
):
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    if not setting_info:
        return await response_code.resp_404()

    await check_setting(bind=bind, id_=api_case, ids=setting_info[0].api_case_ids)
    await check_setting(bind=bind, id_=ui_case, ids=setting_info[0].ui_case_ids)
    await check_setting(bind=bind, id_=host, ids=setting_info[0].host_ids)
    await check_setting(bind=bind, id_=customize, ids=setting_info[0].customize_ids)
    await check_setting(bind=bind, id_=db_, ids=setting_info[0].db_ids)

    return await crud.update_setting_bind(
        db=db,
        id_=setting_id,
        bind=bind,
        api_case=api_case,
        ui_case=ui_case,
        host=host,
        customize=customize,
        db_=db_,
    )


@setting_.delete(
    '/del/setting',
    name='删除环境数据'
)
async def del_setting(setting_id: int, db: Session = Depends(get_db)):
    if not await crud.get_setting(db=db, id_=setting_id):
        return await response_code.resp_404()

    await crud.del_setting(db=db, id_=setting_id)
    return await response_code.resp_200()


"""
获取数据和绑定数据的接口
"""


@setting_.get(
    '/get/case/api',
    name='获取api用例的绑定信息'
)
async def get_case_api(setting_id: int, page: int = 1, size: int = 1000, db: Session = Depends(get_db)):
    # 获取到用例信息
    test_case = await api_crud.get_case_info(db=db, page=page, size=size)

    # 获取配置信息
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    api_case_ids = setting_info[0].api_case_ids

    case_info = []
    for case in test_case:
        temp_info = await temp_crud.get_temp_name(db=db, temp_id=case.temp_id)
        case_info.append(
            {
                "project_name": temp_info[0].project_name,
                "temp_name": temp_info[0].temp_name,
                "case_name": case.case_name,
                "case_id": case.id,
                "bind": True if case.id in api_case_ids else False
            }
        )
    case_info.sort(key=lambda i: i['bind'], reverse=True)
    return case_info


@setting_.get(
    '/get/case/ui',
    name='获取ui用例的绑定信息'
)
async def get_case_ui(setting_id: int, page: int = 1, size: int = 1000, db: Session = Depends(get_db)):
    # 获取到用例信息
    test_case = await ui_crud.get_playwright(db=db, page=page, size=size)

    # 获取配置信息
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    ui_case_ids = setting_info[0].ui_case_ids

    case_info = []
    for case in test_case:
        case_info.append(
            {
                "project_name": case.project_name,
                "case_name": case.temp_name,
                "case_id": case.id,
                "bind": True if case.id in ui_case_ids else False
            }
        )
    case_info.sort(key=lambda i: i['bind'], reverse=True)
    return case_info


@setting_.get(
    '/get/host',
    name='获取host的绑定信息'
)
async def get_host(setting_id: int, db: Session = Depends(get_db)):
    # 获取到用例信息
    host_info = await conf_crud.get_host(db=db)

    # 获取配置信息
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    host_ids = setting_info[0].host_ids

    x_info = []
    for x in host_info:
        x_info.append(
            {
                "name": x.name,
                "host": x.host,
                "id": x.id,
                "bind": True if x.id in host_ids else False
            }
        )

    x_info.sort(key=lambda i: i['bind'], reverse=True)

    return x_info


@setting_.get(
    '/get/customize',
    name='获取customize的绑定信息'
)
async def get_customize(setting_id: int, db: Session = Depends(get_db)):
    # 获取到用例信息
    customize_info = await conf_crud.get_customize(db=db)

    # 获取配置信息
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    customize_ids = setting_info[0].customize_ids

    x_info = []
    for x in customize_info:
        x_info.append(
            {
                "name": x.name,
                "key": x.key,
                "value": x.value,
                "type": x.type,
                "id": x.id,
                "bind": True if x.id in customize_ids else False
            }
        )

    x_info.sort(key=lambda i: i['bind'], reverse=True)

    return x_info


@setting_.get(
    '/get/db',
    name='获取db的绑定信息'
)
async def get_db_(setting_id: int, db: Session = Depends(get_db)):
    # 获取到用例信息
    db_info = await conf_crud.get_db(db=db)

    # 获取配置信息
    setting_info = await crud.get_setting(db=db, id_=setting_id)
    db_ids = setting_info[0].db_ids

    x_info = []
    for x in db_info:
        x_info.append(
            {
                "name": x.name,
                "host": x.host,
                "user": x.user,
                "password": x.password,
                "database": x.database,
                "port": x.port,
                "charset": x.charset,
                "id": x.id,
                "bind": True if x.id in db_ids else False
            }
        )

    x_info.sort(key=lambda i: i['bind'], reverse=True)

    return x_info
