#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/4/16-14:42
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from depends import get_db
from apps.whole_conf import crud, schemas
from apps import response_code
from .tool import check

conf = APIRouter()

"""
域名列表的接口
"""


@conf.post(
    '/add/host',
    name='添加域名',
    response_model=schemas.ConfHostOut
)
async def add_host(conf_host: schemas.ConfHostIn, db: Session = Depends(get_db)):
    if await crud.get_host(db=db, name=conf_host.name):
        return await response_code.resp_400(message='存在相同的name')

    return await crud.create_host(db=db, conf_host=conf_host)


@conf.get(
    '/get/host',
    name='获取域名',
    response_model=List[schemas.ConfHostOut]
)
async def get_host(host_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_host(db=db, id_=host_id)


@conf.put(
    '/update/host',
    name='修改域名',
)
async def update_host(host_id: int, conf_host: schemas.ConfHostIn, db: Session = Depends(get_db)):
    if not await crud.get_host(db=db, id_=host_id):
        return await response_code.resp_404()

    await crud.update_host(db=db, id_=host_id, conf_host=conf_host)
    return await response_code.resp_200()


@conf.delete(
    '/del/host',
    name='删除域名'
)
async def del_host(host_id: int, db: Session = Depends(get_db)):
    if not await crud.get_host(db=db, id_=host_id):
        return await response_code.resp_404()

    await crud.del_host(db=db, id_=host_id)
    return await response_code.resp_200()


"""
项目列表的接口
"""


@conf.post(
    '/add/project',
    name='添加项目',
    response_model=schemas.ConfProjectOut
)
async def add_project(conf_project: schemas.ConfProjectIn, db: Session = Depends(get_db)):
    if await crud.get_project(db=db, name=conf_project.name):
        return await response_code.resp_400(message='存在相同的name')

    return await crud.create_project(db=db, conf_project=conf_project)


@conf.get(
    '/get/project',
    name='获取项目',
    response_model=List[schemas.ConfProjectOut]
)
async def get_project(project_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_project(db=db, id_=project_id)


@conf.put(
    '/update/project',
    name='修改项目',
)
async def update_project(project_id: int, conf_project: schemas.ConfProjectIn, db: Session = Depends(get_db)):
    if not await crud.get_project(db=db, id_=project_id):
        return await response_code.resp_404()

    await crud.update_project(db=db, id_=project_id, conf_project=conf_project)
    return await response_code.resp_200()


@conf.delete(
    '/del/project',
    name='删除项目'
)
async def del_project(project_id: int, db: Session = Depends(get_db)):
    if not await crud.get_project(db=db, id_=project_id):
        return await response_code.resp_404()

    await crud.del_project(db=db, id_=project_id)
    return await response_code.resp_200()


"""
数据库配置列表的接口
"""


@conf.post(
    '/add/db',
    name='添加数据库',
    response_model=schemas.ConfDBOut
)
async def add_db(conf_db: schemas.ConfDBIn, db: Session = Depends(get_db)):
    if await crud.get_db(db=db, name=conf_db.name):
        return await response_code.resp_400(message='存在相同的name')

    return await crud.create_db(db=db, conf_db=conf_db)


@conf.get(
    '/get/db',
    name='获取数据库',
    response_model=List[schemas.ConfDBOut]
)
async def get_db_(db_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_db(db=db, id_=db_id)


@conf.put(
    '/update/db',
    name='修改数据库',
)
async def update_db(db_id: int, conf_db: schemas.ConfDBIn, db: Session = Depends(get_db)):
    if not await crud.get_db(db=db, id_=db_id):
        return await response_code.resp_404()

    await crud.update_db(db=db, id_=db_id, conf_db=conf_db)
    return await response_code.resp_200()


@conf.delete(
    '/del/db',
    name='删除数据库'
)
async def del_db(db_id: int, db: Session = Depends(get_db)):
    if not await crud.get_db(db=db, id_=db_id):
        return await response_code.resp_404()

    await crud.del_db(db=db, id_=db_id)
    return await response_code.resp_200()


"""
统一响应列表的接口
"""


@conf.post(
    '/add/unify',
    name='添加统一响应',
    response_model=schemas.ConfUnifyResOut
)
async def add_unify(conf_unify_res: schemas.ConfUnifyResIn, db: Session = Depends(get_db)):
    if await crud.get_unify_res(db=db, name=conf_unify_res.name):
        return await response_code.resp_400(message='存在相同的name')

    try:
        check(enum=conf_unify_res)
    except TypeError:
        return await response_code.resp_400(message=f"type: {conf_unify_res.type}和value: {conf_unify_res.value} 的类型不对应")

    return await crud.create_unify_res(db=db, conf_unify_res=conf_unify_res)


@conf.get(
    '/get/unify',
    name='获取统一响应',
    response_model=List[schemas.ConfUnifyResOut]
)
async def get_unify(unify_res_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_unify_res(db=db, id_=unify_res_id)


@conf.put(
    '/update/unify',
    name='修改统一响应',
)
async def update_unify(unify_res_id: int, conf_unify_res: schemas.ConfUnifyResIn, db: Session = Depends(get_db)):
    if not await crud.get_unify_res(db=db, id_=unify_res_id):
        return await response_code.resp_404()

    try:
        check(enum=conf_unify_res)
    except TypeError:
        return await response_code.resp_400(message=f"type: {conf_unify_res.type}和value: {conf_unify_res.value} 的类型不对应")

    await crud.update_unify_res(db=db, id_=unify_res_id, conf_unify_res=conf_unify_res)
    return await response_code.resp_200()


@conf.delete(
    '/del/unify',
    name='删除统一响应'
)
async def del_unify(unify_res_id: int, db: Session = Depends(get_db)):
    if not await crud.get_unify_res(db=db, id_=unify_res_id):
        return await response_code.resp_404()

    await crud.del_unify_res(db=db, id_=unify_res_id)
    return await response_code.resp_200()


"""
自定义参数列表的接口
"""


@conf.post(
    '/add/customize',
    name='添加自定义参数',
    response_model=schemas.ConfCustomizeOut
)
async def add_customize(conf_customize: schemas.ConfCustomizeIn, db: Session = Depends(get_db)):
    if await crud.get_customize(db=db, name=conf_customize.name):
        return await response_code.resp_400(message='存在相同的name')

    try:
        check(enum=conf_customize)
    except TypeError:
        return await response_code.resp_400(message=f"type: {conf_customize.type}和value: {conf_customize.value} 的类型不对应")
    return await crud.create_customize(db=db, conf_customize=conf_customize)


@conf.get(
    '/get/customize',
    name='获取自定义参数',
    response_model=List[schemas.ConfCustomizeOut]
)
async def get_customize(customize_id: int = None, db: Session = Depends(get_db)):
    return await crud.get_customize(db=db, id_=customize_id)


@conf.put(
    '/update/customize',
    name='修改自定义参数',
)
async def update_customize(customize_id: int, conf_customize: schemas.ConfCustomizeIn, db: Session = Depends(get_db)):
    if not await crud.get_customize(db=db, id_=customize_id):
        return await response_code.resp_404()

    try:
        check(enum=conf_customize)
    except TypeError:
        return await response_code.resp_400(message=f"type: {conf_customize.type}和value: {conf_customize.value} 的类型不对应")

    await crud.update_customize(db=db, id_=customize_id, conf_customize=conf_customize)
    return await response_code.resp_200()


@conf.delete(
    '/del/customize',
    name='删除自定义参数'
)
async def del_customize(customize_id: int, db: Session = Depends(get_db)):
    if not await crud.get_customize(db=db, id_=customize_id):
        return await response_code.resp_404()

    await crud.del_customize(db=db, id_=customize_id)
    return await response_code.resp_200()
