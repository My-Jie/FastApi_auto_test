#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/2/25-21:07
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps import response_code
from apps.case_service import crud as c_crud
from apps.own_params_rep import schemas, crud
from apps.template import crud as t_crud
from apps.template import schemas as t_schemas
from depends import get_db
from .tool import dict_add, dict_edit, dict_del

own_rep = APIRouter()


@own_rep.get(
    '/url/for/data',
    name='通过url+method查找相同接口数据',
    response_model=List[t_schemas.TempChangeParams]
    # response_model_exclude=['headers', 'file_data', 'response'],
)
async def url_for_data(method: str, path: str, db: Session = Depends(get_db)):
    """
    通过url+method，查询出模板的信息，以及关联的用例信息
    """
    path = path.replace('*', '%')
    temp_info = await crud.get_all_url_method(db=db, method=method.upper(), path=path.strip())
    return [{
        'temp_id': x[0],
        'temp_name': x[1],
        'number': x[2],
        'path': x[3],
        'params': x[4],
        'data': x[5],
    } for x in temp_info] if temp_info else await response_code.resp_404()


@own_rep.get(
    '/temp/for/casedata',
    name='通过模板id和number获取用例id和number和其他信息'
)
async def temp_for_case_data(temp_id: int, number: int, db: Session = Depends(get_db)):
    """
    通过模板id和number获取用例信息
    """
    db_info = await crud.get_temp_fo_case_info(db=db, temp_id=temp_id, number=number)
    return [{
        'case_id': x[0],
        'number': x[1],
        'path': x[2],
        'params': x[3],
        'data': x[4],
    } for x in db_info] if db_info else await response_code.resp_400()


@own_rep.put(
    '/url/edit',
    name='修改url',
)
async def url_edit(ue: schemas.UrlEdit, db: Session = Depends(get_db)):
    if ue.temp_id and ue.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if ue.temp_id:
        template_data = await t_crud.get_temp_name(db=db, temp_id=ue.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if ue.rep_url:
            await crud.temp_rep_url_edit(
                db=db,
                temp_id=ue.temp_id,
                number=ue.number,
                old_url=ue.old_url.strip(),
                new_url=ue.new_url.strip()
            )
        else:
            await crud.temp_rep_url_edit(
                db=db,
                temp_id=ue.temp_id,
                number=ue.number,
                old_url=ue.new_url.strip(),
                new_url=ue.old_url.strip()
            )

        return await response_code.resp_200()

    if ue.case_id:
        case_info = await c_crud.get_case_info(db=db, case_id=ue.case_id)
        if not case_info:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if ue.rep_url:
            await crud.case_rep_url_edit(
                db=db,
                case_id=ue.case_id,
                number=ue.number,
                old_url=ue.old_url.strip(),
                new_url=ue.new_url.strip()
            )
        else:
            await crud.case_rep_url_edit(
                db=db,
                case_id=ue.case_id,
                number=ue.number,
                old_url=ue.new_url.strip(),
                new_url=ue.old_url.strip()
            )

        return await response_code.resp_200()

    return await response_code.resp_400(message='操作无效')


@own_rep.put(
    '/params/add',
    name='params添加字段'
)
async def params_add(pa: schemas.ParamsAdd, db: Session = Depends(get_db)):
    if pa.temp_id and pa.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if pa.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=pa.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if pa.rep_params_add:
            try:
                seek_key, insert_key = pa.key.split('.', 1)
            except ValueError:
                seek_key, insert_key = None, pa.key
            new_params = dict_add(
                seek_key=seek_key,
                insert_key=insert_key,
                value=pa.value,
                dict_data=template_data[pa.number].params
            )
            await crud.temp_set_json(db=db, temp_id=pa.temp_id, number=pa.number, params=new_params)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    if pa.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=pa.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if pa.rep_params_add:
            try:
                seek_key, insert_key = pa.key.split('.', 1)
            except ValueError:
                seek_key, insert_key = None, pa.key
            new_params = dict_add(
                seek_key=seek_key,
                insert_key=insert_key,
                value=pa.value,
                dict_data=case_data[pa.number].params
            )
            await crud.case_set_json(db=db, case_id=pa.case_id, number=pa.number, params=new_params)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    return await response_code.resp_400(message='操作无效')


@own_rep.put(
    '/params/edit',
    name='params修改字段'
)
async def params_edit(pe: schemas.ParamsEdit, db: Session = Depends(get_db)):
    if pe.temp_id and pe.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if pe.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=pe.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if pe.rep_params_edit:
            new_params = dict_edit(
                old_key=pe.old_key,
                new_key=pe.new_key,
                dict_data=template_data[pe.number].params,
                value=pe.value
            )
        else:
            new_params = dict_edit(
                old_key=pe.new_key,
                new_key=pe.old_key,
                dict_data=template_data[pe.number].params,
                value=pe.value
            )

        await crud.temp_set_json(db=db, temp_id=pe.temp_id, number=pe.number, params=new_params)
        return await response_code.resp_200()

    if pe.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=pe.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if pe.rep_params_edit:
            new_params = dict_edit(
                old_key=pe.old_key,
                new_key=pe.new_key,
                dict_data=case_data[pe.number].params,
                value=pe.value
            )
        else:
            new_params = dict_edit(
                old_key=pe.new_key,
                new_key=pe.old_key,
                dict_data=case_data[pe.number].params,
                value=pe.value
            )

        await crud.case_set_json(db=db, case_id=pe.case_id, number=pe.number, params=new_params)
        return await response_code.resp_200()

    return await response_code.resp_400(message='操作无效')


@own_rep.put(
    '/params/del',
    name='params删除字段'
)
async def params_del(pd: schemas.ParamsDel, db: Session = Depends(get_db)):
    if pd.temp_id and pd.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if pd.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=pd.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if pd.rep_params_del:
            new_params = dict_del(old_key=pd.key, dict_data=template_data[pd.number].params)
            await crud.temp_set_json(db=db, temp_id=pd.temp_id, number=pd.number, params=new_params)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    if pd.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=pd.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if pd.rep_params_del:
            new_params = dict_del(old_key=pd.key, dict_data=case_data[pd.number].params)
            await crud.case_set_json(db=db, case_id=pd.case_id, number=pd.number, params=new_params)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    return await response_code.resp_400(message='操作无效')


#######################################################################################################################

@own_rep.put(
    '/data/add',
    name='data添加字段'
)
async def data_add(da: schemas.DataAdd, db: Session = Depends(get_db)):
    if da.temp_id and da.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if da.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=da.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if da.rep_data_add:
            try:
                seek_key, insert_key = da.key.split('.', 1)
            except ValueError:
                seek_key, insert_key = None, da.key
            new_data = dict_add(
                seek_key=seek_key,
                insert_key=insert_key,
                value=da.value,
                dict_data=template_data[da.number].data
            )
            await crud.temp_set_json(db=db, temp_id=da.temp_id, number=da.number, data=new_data)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    if da.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=da.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if da.rep_data_add:
            try:
                seek_key, insert_key = da.key.split('.', 1)
            except ValueError:
                seek_key, insert_key = None, da.key
            new_data = dict_add(
                seek_key=seek_key,
                insert_key=insert_key,
                value=da.value,
                dict_data=case_data[da.number].data
            )
            await crud.case_set_json(db=db, case_id=da.case_id, number=da.number, data=new_data)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    return await response_code.resp_400(message='操作无效')


@own_rep.put(
    '/data/edit',
    name='data修改字段'
)
async def data_edit(de: schemas.DataEdit, db: Session = Depends(get_db)):
    if de.temp_id and de.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if de.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=de.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if de.rep_data_edit:
            new_data = dict_edit(
                old_key=de.old_key,
                new_key=de.new_key,
                dict_data=template_data[de.number].data,
                value=de.value
            )
        else:
            new_data = dict_edit(
                old_key=de.new_key,
                new_key=de.old_key,
                dict_data=template_data[de.number].data,
                value=de.value
            )

        await crud.temp_set_json(db=db, temp_id=de.temp_id, number=de.number, data=new_data)
        return await response_code.resp_200()

    if de.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=de.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if de.rep_data_edit:
            new_data = dict_edit(
                old_key=de.old_key,
                new_key=de.new_key,
                dict_data=case_data[de.number].data,
                value=de.value
            )
        else:
            new_data = dict_edit(
                old_key=de.new_key,
                new_key=de.old_key,
                dict_data=case_data[de.number].data,
                value=de.value
            )
        await crud.case_set_json(db=db, case_id=de.case_id, number=de.number, data=new_data)
        return await response_code.resp_200()

    return await response_code.resp_400(message='操作无效')


@own_rep.put(
    '/data/del',
    name='data删除字段'
)
async def data_del(dd: schemas.DataDel, db: Session = Depends(get_db)):
    if dd.temp_id and dd.case_id:
        return await response_code.resp_400(message='temp_id和case_id不能同时存在')

    if dd.temp_id:
        template_data = await t_crud.get_template_data(db=db, temp_id=dd.temp_id)
        if not template_data:
            return await response_code.resp_404(message='没有获取到这个模板id')

        if dd.rep_data_del:
            new_data = dict_del(old_key=dd.key, dict_data=template_data[dd.number].data)
            await crud.temp_set_json(db=db, temp_id=dd.temp_id, number=dd.number, data=new_data)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    if dd.case_id:
        case_data = await c_crud.get_case_data(db=db, case_id=dd.case_id)
        if not case_data:
            return await response_code.resp_404(message='没有获取到这个用例id')

        if dd.rep_data_del:
            new_data = dict_del(old_key=dd.key, dict_data=case_data[dd.number].data)
            await crud.case_set_json(db=db, case_id=dd.case_id, number=dd.number, data=new_data)
            return await response_code.resp_200()
        else:
            return await response_code.resp_400(message='操作不可逆')

    return await response_code.resp_400(message='操作无效')
