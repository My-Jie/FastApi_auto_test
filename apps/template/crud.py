#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/8-10:19
"""

import datetime
from typing import List
from sqlalchemy import func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from apps.template import models, schemas
from apps.case_service import models as case_models
from apps.whole_conf import models as conf_models
from apps.api_report import models as report_models


async def create_template(db: AsyncSession, temp_name: str, project_name: int):
    """
    创建模板信息
    :param db:
    :param temp_name:
    :param project_name:
    :return:
    """
    db_temp = models.Template(temp_name=temp_name, project_name=project_name)
    db.add(db_temp)
    await db.commit()
    await db.refresh(db_temp)
    return db_temp


async def update_template(db: AsyncSession, temp_id: int, api_count: int = None):
    """
    更新模板信息
    :param db:
    :param temp_id:
    :param api_count:
    :return:
    """
    result = await db.execute(
        select(models.Template).where(models.Template.id == temp_id)
    )
    db_temp = result.scalars().first()
    if db_temp:
        db_temp.api_count = api_count
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def create_template_data(db: AsyncSession, data: List[dict], temp_id: int):
    """
    创建模板数据集
    :param db:
    :param data:
    :param temp_id:
    :return:
    """
    for x in data:
        d = schemas.TemplateDataIn(**x)
        db_data = models.TemplateData(**d.dict(), temp_id=temp_id)
        db.add(db_data)
    await db.commit()


async def create_template_data_add(db: AsyncSession, data: schemas.TemplateDataInTwo):
    """
    创建模板数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TemplateData(**data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def update_template_data(db: AsyncSession, temp_id: int, id_: int, new_number: int, old_number: int = None):
    """
    更新模板信息
    :param db:
    :param temp_id:
    :param old_number:
    :param new_number:
    :param id_:
    :return:
    """
    if old_number:
        result = await db.execute(
            select(models.TemplateData).where(
                models.TemplateData.id == id_,
                models.TemplateData.temp_id == temp_id,
                models.TemplateData.number == old_number
            )
        )
        db_temp = result.scalars().first()
    else:
        result = await db.execute(
            select(models.TemplateData).where(
                models.TemplateData.id == id_,
                models.TemplateData.temp_id == temp_id,
            )
        )
        db_temp = result.scalars().first()

    if db_temp:
        db_temp.number = new_number
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def get_temp_name(
        db: AsyncSession,
        temp_name: str = None,
        temp_id: int = None,
        page: int = 1,
        size: int = 10
):
    """
    按模板名称查询数据
    :param db:
    :param temp_name:
    :param temp_id:
    :param page:
    :param size:
    :return:
    """
    if temp_id is not None:
        result = await db.execute(
            select(models.Template).where(models.Template.id == temp_id).order_by(models.Template.id.desc())
        )
        return result.scalars().all()

    if temp_name:
        result = await db.execute(
            select(models.Template).where(models.Template.temp_name == temp_name).order_by(
                models.Template.id.desc()
            )
        )
        return result.scalars().all()

    result = await db.execute(
        select(models.Template).order_by(models.Template.id.desc()).offset(size * (page - 1)).limit(size)
    )
    return result.scalars().all()


async def get_temp_case_info(db: AsyncSession, temp_id: int, outline: bool):
    """
    查询模板下有多少条用例
    :param db:
    :param temp_id:
    :param outline:
    :return:
    """
    result = await db.execute(
        select(case_models.TestCase).where(case_models.TestCase.temp_id == temp_id).order_by(
            case_models.TestCase.id
        )
    )
    db_case = result.scalars().all()
    case_info = []
    for case in db_case:
        if outline is False:
            result = await db.execute(
                select(report_models.ApiReportList).where(
                    report_models.ApiReportList.case_id == case.id,
                ).order_by(
                    report_models.ApiReportList.id.desc()
                )
            )
            report = result.scalars().first()
            case_info.append({
                'id': case.id,
                'mode': case.mode,
                'name': case.case_name,
                'run_num': case.run_order,
                'success': case.success,
                'fail': case.fail,
                'created_at': report.created_at if report else '1970-01-01 00:00:00',
            })
        else:
            case_info.append({'id': case.id, 'name': case.case_name})

    return {'case_count': len(db_case), 'case_info': case_info} if outline is False else {'case_info': case_info}


async def get_template_data(db: AsyncSession, temp_id: int = None, numbers: list = None):
    """
    查询模板数据
    :param db:
    :param temp_id:
    :param numbers:
    :return:
    """

    if temp_id and numbers:
        result = await db.execute(
            select(models.TemplateData).where(
                models.TemplateData.temp_id == temp_id,
                models.TemplateData.number.in_(numbers),
            ).order_by(
                models.TemplateData.number
            )
        )
        return result.scalars().all()

    if temp_id:
        result = await db.execute(
            select(models.TemplateData).where(models.TemplateData.temp_id == temp_id).order_by(
                models.TemplateData.number
            )
        )
        return result.scalars().all()


async def get_tempdata_detail(db: AsyncSession, detail_id: int, temp_name: bool = None):
    """
    查询模板数据
    :param db:
    :param detail_id:
    :param temp_name:
    :return:
    """
    if temp_name:
        result = await db.execute(
            select(models.TemplateData, models.Template).where(
                models.TemplateData.id == detail_id,
            ).where(
                models.TemplateData.temp_id == models.Template.id
            )
        )
        return result.first()

    result = await db.execute(
        select(models.TemplateData).where(models.TemplateData.id == detail_id)
    )
    return result.scalars().first()


async def get_temp_host(db: AsyncSession, temp_id: int):
    """
    查询模板数据
    :param db:
    :param temp_id:
    :return:
    """
    result = await db.execute(
        select(models.TemplateData.host).where(models.TemplateData.temp_id == temp_id).order_by(
            models.TemplateData.number
        )
    )
    return result.all()


async def put_temp_name(db: AsyncSession, new_name: str, temp_id: int = None, old_name: str = None):
    """
    更新模板名称
    :param db:
    :param temp_id:
    :param old_name:
    :param new_name:
    :return:
    """
    db_temp = None

    if temp_id:
        result = await db.execute(
            select(models.Template).where(models.Template.id == temp_id)
        )
        db_temp = result.scalars().first()

    if old_name:
        result = await db.execute(
            select(models.Template).where(models.Template.temp_name == old_name)
        )
        db_temp = result.scalars().first()

    if db_temp:
        db_temp.temp_name = new_name
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def put_description(db: AsyncSession, new_description: str, api_id: int):
    """
    更新模板描述
    :param db:
    :param new_description:
    :param api_id:
    :return:
    """
    result = await db.execute(
        select(models.TemplateData).where(models.TemplateData.id == api_id)
    )
    db_temp = result.scalars().first()
    if db_temp:
        db_temp.description = new_description
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def del_template_data_all(db: AsyncSession, temp_name: str = None, temp_id: int = None):
    """
    删除所有模板数据
    :param db:
    :param temp_name:
    :param temp_id:
    :return:
    """
    db_temp = None
    if temp_name:
        result = await db.execute(
            select(models.Template).where(models.Template.temp_name == temp_name)
        )
        db_temp = result.scalars().first()

    if temp_id:
        result = await db.execute(
            select(models.Template).where(models.Template.id == temp_id)
        )
        db_temp = result.scalars().first()

    if db_temp:
        await db.execute(
            delete(models.TemplateData).filter(models.TemplateData.temp_id == db_temp.id)
        )
        await db.execute(
            delete(models.Template).filter(models.Template.id == db_temp.id)
        )
        await db.commit()
        return db_temp


async def del_template_data(db: AsyncSession, temp_id: int, number: int):
    """
    删除部分数据
    :param db:
    :param temp_id:
    :param number:
    :return:
    """
    await db.execute(
        delete(models.TemplateData).filter(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number == number
        )
    )
    await db.commit()


async def get_all_temp_name(db: AsyncSession, temp_ids):
    """
    获取所有的模板名称
    :param db:
    :param temp_ids:
    :return:
    """
    result = await db.execute(
        select(models.Template.temp_name).where(models.Template.id.in_(temp_ids))
    )
    return result.scalars().all()


async def get_new_temp_info(db: AsyncSession, temp_id: int, number: int, method: str):
    """

    :param db:
    :param temp_id:
    :param number:
    :param method:
    :return:
    """
    result = await db.execute(
        select(models.TemplateData).where(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number == number,
            models.TemplateData.method == method
        ).order_by(
            models.TemplateData.number
        )
    )
    return result.scalars().first()


async def get_temp_all(db: AsyncSession):
    """
    查询所有模板数据
    :param db:
    :return:
    """
    result = await db.execute(
        select(models.TemplateData).order_by(
            models.TemplateData.temp_id,
            models.TemplateData.number,
            models.TemplateData.method,
            models.TemplateData.path
        ).order_by(
            models.TemplateData.id
        )
    )
    return result.scalars().all()


async def update_api_info(db: AsyncSession, api_info: schemas.TemplateDataInTwo):
    """
    修改用例api信息
    :param db:
    :param api_info:
    :return:
    """
    if not await get_template_data(db=db, temp_id=api_info.temp_id, numbers=[api_info.number]):
        return False

    await db.execute(
        update(models.TemplateData).filter(
            models.TemplateData.temp_id == api_info.temp_id,
            models.TemplateData.number == api_info.number
        ).values({
            'host': api_info.host,
            'path': api_info.path,
            'code': api_info.code,
            'method': api_info.method,
            'params': api_info.params,
            'json_body': api_info.json_body,
            'data': api_info.data,
            'headers': api_info.headers,
            'response': api_info.response,
            'description': api_info.description,
        })
    )
    await db.commit()
    return True


async def get_temp_numbers(db: AsyncSession, temp_id: int, number: int):
    """
    查询某个number后的模板数据
    :param db:
    :param temp_id:
    :param number:
    :return:
    """
    result = await db.execute(
        select(models.TemplateData).where(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number >= number
        ).order_by(
            models.TemplateData.number.desc()
        )
    )
    return result.scalars().all()


async def get_count(db: AsyncSession, temp_name: str = None, today: bool = None):
    """
    记数查询
    :param db:
    :param temp_name:
    :param today:
    :return:
    """
    if temp_name:
        result = await db.execute(
            select(func.count(models.Template.id)).where(
                models.Template.temp_name.like(f"%{temp_name}%")
            )
        )
        return result.scalar()

    if today:
        result = await db.execute(
            select(func.count(models.Template.id)).where(
                models.Template.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.Template.id))
    )
    return result.scalar()


async def get_api_count(db: AsyncSession, today: bool = None):
    """
    记数查询
    :param db:
    :param today:
    :return:
    """
    if today:
        result = await db.execute(
            select(func.count(models.TemplateData.id)).where(
                models.TemplateData.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.TemplateData.id))
    )
    return result.scalar()


async def save_temp_info(
        db: AsyncSession,
        temp_id: int = None,
        number: int = None,
        detail_id: int = None,
        params: dict = None,
        data: dict = None,
        headers: dict = None,
        json_body: str = None,
        api_type: str = ''
):
    """
    更新用例的数据
    """
    if detail_id:
        if api_type == 'API模板':
            result = await db.execute(select(models.TemplateData).where(models.TemplateData.id == detail_id))
        else:
            result = await db.execute(select(case_models.TestCaseData).where(case_models.TestCaseData.id == detail_id))
        db_temp = result.scalars().first()
    else:
        result = await db.execute(
            select(models.TemplateData).where(
                models.TemplateData.temp_id == temp_id,
                models.TemplateData.number == number,
            )
        )
        db_temp = result.scalars().first()

    if db_temp:
        if params is not None:
            db_temp.params = params
            flag_modified(db_temp, "params")

        elif data is not None:
            db_temp.data = data
            flag_modified(db_temp, "data")

        elif headers is not None:
            db_temp.headers = headers
            flag_modified(db_temp, "headers")

        if json_body:
            db_temp.json_body = json_body

        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def save_path_info(db: AsyncSession, temp_id: int, number: int, api_path: dict):
    """
    更新用例的path
    """
    result = await db.execute(
        select(models.TemplateData).where(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number == number,
        )
    )
    db_temp = result.scalars().first()

    if db_temp:
        db_temp.method = api_path['method']
        db_temp.path = api_path['path']
        db_temp.code = api_path['code']
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def sync_temp(
        db: AsyncSession,
        number: int,
        method: str,
        path: str,
        data_type: str,
        temp_id: int = None,
        temp_all: bool = False
):
    """
    按method+path查询模板的数据
    :param db:
    :param number:
    :param method:
    :param path:
    :param data_type:
    :param temp_all: 没传temp_all就查询当前模板的数据， 传就查询所有
    :param temp_id:
    :return:
    """
    if not temp_all:
        result = await db.execute(
            select(models.TemplateData, models.Template).where(
                models.TemplateData.temp_id == temp_id,
                models.TemplateData.method == method,
                models.TemplateData.path == path,
            ).filter(
                models.TemplateData.temp_id == models.Template.id
            )
        )
        db_temp = result.all()
    else:
        result = await db.execute(
            select(models.TemplateData, models.Template).where(
                models.TemplateData.method == method,
                models.TemplateData.path == path,
            ).filter(
                models.TemplateData.temp_id == models.Template.id
            )
        )
        db_temp = result.all()

    temp_list = []
    for x in db_temp:
        if not (x[0].temp_id == temp_id and x[0].number == number):
            # if any([
            #     x[0].temp_id == temp_id and x[0].number != number,
            #     x[0].temp_id != temp_id and x[0].number == number
            # ]):
            temp_list.append(
                {
                    'id': x[0].id,
                    'temp_id': x[0].temp_id,
                    'number': x[0].number,
                    'method': x[0].method,
                    'path': x[0].path,
                    'data': {
                        'params': x[0].params,
                        'data': x[0].data,
                        'headers': x[0].headers
                    }.get(data_type),
                    'description': x[0].description,
                    'active_name': '4',
                    'type': data_type,
                    'temp_name': x[1].temp_name,
                    'source': 'API模板'
                }
            )

    return temp_list


async def get_temp_data_group(db: AsyncSession, temp_ids: List[int]):
    """
    获取模板分组
    :param db:
    :param temp_ids:
    :return:
    """
    result = await db.execute(
        select(models.Template, models.TemplateData).filter(
            models.TemplateData.temp_id.in_(temp_ids),
            models.Template.id == models.TemplateData.temp_id
        ).order_by(
            models.TemplateData.temp_id
        )
    )
    return result.all()


async def get_temp_all_info(
        db: AsyncSession,
        temp_name: str = '',
        page: int = 1,
        size: int = 10
):
    result = await db.execute(
        select(
            models.Template,
            conf_models.ConfProject.code
        ).filter(
            models.Template.temp_name.like(f"%{temp_name}%"),
            models.Template.project_name == conf_models.ConfProject.id
        ).order_by(
            models.Template.id.desc()
        ).offset(size * (page - 1)).limit(size)
    )
    return result.all()
