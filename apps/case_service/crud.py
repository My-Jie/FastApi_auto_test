#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/20-21:59
"""

import datetime
from tools import rep_value, rep_url
from sqlalchemy import func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from apps.case_service import models, schemas
from apps.whole_conf import models as conf_models
from apps.template import models as temp_models
from apps.api_report import models as report_models

from typing import List


async def create_test_case(db: AsyncSession, case_name: str, mode: str, temp_id: int):
    """
    创建测试数据
    :param db:
    :param case_name:
    :param mode:
    :param temp_id:
    :return:
    """
    db_case = models.TestCase(case_name=case_name, mode=mode, temp_id=temp_id)
    db.add(db_case)
    await db.commit()
    await db.refresh(db_case)
    return db_case


async def update_test_case(db: AsyncSession, case_id: int, case_count: int = None):
    """
    更新测试信息
    :param db:
    :param case_id:
    :param case_count:
    :return:
    """
    result = await db.execute(
        select(models.TestCase).filter(models.TestCase.id == case_id)
    )
    db_temp = result.scalars().first()
    if db_temp:
        db_temp.case_count = case_count
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def create_test_case_data(db: AsyncSession, data: schemas.TestCaseDataIn, case_id: int):
    """
    创建测试数据集
    :param db:
    :param data:
    :param case_id:
    :return:
    """
    db_data = models.TestCaseData(**data.dict(), case_id=case_id)
    db.add(db_data)
    # await db.commit()
    # await db.refresh(db_data)
    # return db_data


async def create_test_case_data_add(db: AsyncSession, data: schemas.TestCaseDataInTwo):
    """
    创建测试数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TestCaseData(**data.dict())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data


async def del_test_case_data(db: AsyncSession, case_id: int, number: int = None):
    """
    删除测试数据，不删除用例
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    if number:
        await db.execute(
            delete(
                models.TestCaseData
            ).where(
                models.TestCaseData.case_id == case_id,
                models.TestCaseData.number == number
            )
        )
        await db.commit()
        return

    await db.execute(
        delete(models.TestCaseData).where(models.TestCaseData.case_id == case_id)
    )
    await db.commit()


async def get_case_info(
        db: AsyncSession,
        case_id: int = None,
        page: int = 1,
        size: int = 10
):
    """
    按用例名称查询数据
    :param db:
    :param case_id:
    :param page:
    :param size::
    :return:
    """
    if case_id is not None:
        result = await db.execute(
            select(models.TestCase).filter(models.TestCase.id == case_id).order_by(models.TestCase.id.desc())
        )
        return result.scalars().all()

    if page and size:
        result = await db.execute(
            select(models.TestCase).order_by(models.TestCase.id.desc()).offset(size * (page - 1)).limit(size)
        )
        return result.scalars().all()


async def get_case_data(db: AsyncSession, case_id: int, number: int = None):
    """
    查询测试用例数据
    :param db:
    :param case_id:
    :param number:
    :return:
    """

    if number:
        result = await db.execute(
            select(models.TestCaseData).filter(
                models.TestCaseData.case_id == case_id,
                models.TestCaseData.number == number
            ).order_by(
                models.TestCaseData.number
            )
        )
        return result.scalars().all()
    else:
        result = await db.execute(
            select(models.TestCaseData).filter(models.TestCaseData.case_id == case_id).order_by(
                models.TestCaseData.number
            ))
        return result.scalars().all()


async def set_case_info(
        db: AsyncSession,
        case_id: int,
        number: int,
        config: dict = None,
        check: dict = None,
        params: dict = None,
        data: dict = None,
        headers: dict = None,
):
    """
    更新用例的数据
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number,
        )
    )
    db_temp = result.scalars().first()

    if db_temp:
        if config is not None:
            for k, v in config.items():
                db_temp.config[k] = v
            flag_modified(db_temp, "config")

        elif check is not None:
            for k, v in check.items():
                db_temp.check[k] = v
            flag_modified(db_temp, "check")

        elif params is not None:
            db_temp.params = params
            flag_modified(db_temp, "params")

        elif data is not None:
            db_temp.data = data
            flag_modified(db_temp, "data")

        elif headers is not None:
            db_temp.headers = headers
            flag_modified(db_temp, "headers")

        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def set_case_description(db: AsyncSession, case_id: int, number: int, description: str):
    """
    设置用例描述信息
    :param db:
    :param case_id:
    :param number:
    :param description:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number,
        )
    )
    db_temp = result.scalars().first()

    if db_temp:
        db_temp.description = description
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def set_case_data(
        db: AsyncSession,
        case_id: int,
        number: int,
        old_data: str,
        new_data: str,
        type_: str
):
    """
    替换测试数据
    :param db:
    :param case_id:
    :param number:
    :param old_data:
    :param new_data:
    :param type_:
    :return:
    """

    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number,
        )
    )
    db_temp = result.scalars().first()

    if type_ == 'data':
        new_json = rep_value(json_data=db_temp.data, old_str=old_data, new_str=new_data)
        db_temp.data = new_json
        flag_modified(db_temp, "data")
        await db.commit()
        await db.refresh(db_temp)
        return db_temp
    elif type_ == 'params':
        new_json = rep_value(json_data=db_temp.params, old_str=old_data, new_str=new_data)
        db_temp.params = new_json
        flag_modified(db_temp, "params")
        await db.commit()
        await db.refresh(db_temp)
        return db_temp
    elif type_ == 'headers':
        new_json = rep_value(json_data=db_temp.headers, old_str=old_data, new_str=new_data)
        db_temp.headers = new_json
        flag_modified(db_temp, "headers")
        await db.commit()
        await db.refresh(db_temp)
        return db_temp
    else:
        new_url = rep_url(url=db_temp.path, old_str=old_data, new_str=new_data)
        db_temp.path = new_url
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def del_case_data(db: AsyncSession, case_id: int):
    """
    删除测试数据
    :param db:
    :param case_id:
    :return:
    """
    await db.execute(
        delete(models.TestCase).where(models.TestCase.id == case_id)
    )
    await db.execute(
        delete(models.TestCaseData).where(models.TestCaseData.case_id == case_id)
    )
    await db.commit()


async def get_case(db: AsyncSession, temp_id: int):
    """
    按模板查用例
    :param db:
    :param temp_id:
    :return:
    """
    result = await db.execute(
        select(models.TestCase).filter(models.TestCase.temp_id == temp_id)
    )
    return result.scalars().all()


async def get_case_ids(db: AsyncSession, temp_ids: List[int]):
    """
    按模板查用例id
    :param db:
    :param temp_ids:
    :return:
    """
    result = await db.execute(
        select(models.TestCase.temp_id, models.TestCase.id).filter(
            models.TestCase.temp_id.in_(temp_ids)
        ).order_by(models.TestCase.temp_id)
    )

    return result.all()


async def get_urls(db: AsyncSession, url: str):
    """
    模糊查询url
    :param db:
    :param url:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(models.TestCaseData.path.like(f"{url}%")).order_by(
            models.TestCaseData.number
        )
    )
    return result.scalars().all()


async def update_urls(db: AsyncSession, old_url: str, new_url: str):
    """
    按url查询数据
    :param db:
    :param old_url:
    :param new_url:
    :return:
    """
    if not await get_urls(db=db, url=old_url):
        return None

    result = await db.execute(
        select(models.TestCaseData).filter(models.TestCaseData.path.like(f"{old_url}%")).order_by(
            models.TestCaseData.number
        )
    )
    db_info = result.scalars().all()

    url_info = []
    for info in db_info:
        info.path = new_url
        await db.commit()
        await db.refresh(info)
        url_info.append(info)
    return url_info


async def get_api_info(db: AsyncSession, case_id: int, number: int):
    """
    查询用例api信息
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number,
        )
    )
    return result.scalars().first()


async def update_api_info(db: AsyncSession, api_info: schemas.TestCaseDataOut1):
    """
    修改用例api信息
    :param db:
    :param api_info:
    :return:
    """
    if not await get_api_info(db=db, case_id=api_info.case_id, number=api_info.number):
        return False

    await db.execute(
        update(models.TestCaseData).where(
            models.TestCaseData.case_id == api_info.case_id,
            models.TestCaseData.number == api_info.number
        ).values(api_info.dict())
    )
    await db.commit()
    return True


async def update_api_number(db: AsyncSession, case_id: int, id_: int, new_number: int):
    """
    更新用例的number
    :param db:
    :param case_id:
    :param id_:
    :param new_number:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.id == id_,
            models.TestCaseData.case_id == case_id,
        )
    )
    db_temp = result.scalars().first()

    if db_temp:
        db_temp.number = new_number
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def put_case_name(db: AsyncSession, case_id: int, new_name: str):
    """
    更新用例名称
    :param db:
    :param case_id:
    :param new_name:
    :return:
    """
    db_temp = None

    if case_id:
        result = await db.execute(
            select(models.TestCase).filter(models.TestCase.id == case_id)
        )
        db_temp = result.scalars().first()

    if db_temp:
        db_temp.case_name = new_name
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def get_case_numbers(db: AsyncSession, case_id: int, number: int):
    """
    查询某个number后的用例数据
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number >= number
        ).order_by(
            models.TestCaseData.number
        ).order_by(
            models.TestCaseData.id.desc()
        )
    )
    return result.scalars().all()


async def get_count(db: AsyncSession, case_name: str = None, today: bool = None):
    """
    记数查询
    :param db:
    :param case_name:
    :param today:
    :return:
    """
    if case_name:
        result = await db.execute(
            select(func.count(models.TestCase.id)).filter(
                models.TestCase.case_name.like(f"%{case_name}%")
            )
        )
        return result.scalar()

    if today:
        result = await db.execute(
            select(func.count(models.TestCase.id)).filter(
                models.TestCase.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.TestCase.id))
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
            select(func.count(models.TestCaseData.id)).filter(
                models.TestCaseData.created_at >= datetime.datetime.now().date()
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.TestCaseData.id))
    )
    return result.scalar()


async def get_case_detail(db: AsyncSession, detail_id: int, ):
    """
    查询模板数据
    :param db:
    :param detail_id:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.id == detail_id,
        )
    )
    return result.scalars().first()


async def update_case_path(db: AsyncSession, detail_id: int, new_path: str):
    """
    更新用例path
    :param db:
    :param detail_id:
    :param new_path:
    :return:
    """
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.id == detail_id,
        )
    )
    db_temp = result.scalars().first()
    if db_temp:
        db_temp.path = new_path
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def get_case_info_to_number(
        db: AsyncSession,
        case_id: int,
        numbers: (tuple, list),
):
    result = await db.execute(
        select(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number.in_(numbers)
        )
    )
    return result.scalars().all()


async def get_case_data_group(db: AsyncSession, case_ids: List[int]):
    result = await db.execute(
        select(models.TestCase, models.TestCaseData).filter(
            models.TestCaseData.case_id.in_(case_ids),
            models.TestCase.id == models.TestCaseData.case_id
        )
    )
    return result.all()


async def get_case_all_info(
        db: AsyncSession,
        case_name: str = '',
        page: int = 1,
        size: int = 10
):
    # 内部查询
    inner_sel = select(report_models.ApiReportList).order_by(report_models.ApiReportList.created_at.desc())
    inner_sel_subquery = inner_sel.subquery()
    outer_sel = select(inner_sel_subquery.c).group_by(inner_sel_subquery.c.case_id)
    outer_sel_subquery = outer_sel.subquery()

    result = await db.execute(
        select(
            models.TestCase,
            temp_models.Template.temp_name,
            conf_models.ConfProject.code,
            outer_sel_subquery.c.created_at
        ).join(
            temp_models.Template,
            models.TestCase.temp_id == temp_models.Template.id,
            isouter=True
        ).join(
            conf_models.ConfProject,
            temp_models.Template.project_name == conf_models.ConfProject.id,
            isouter=True
        ).join(
            outer_sel_subquery,
            models.TestCase.id == outer_sel_subquery.c.case_id,
            isouter=True
        ).filter(
            models.TestCase.case_name.like(f"%{case_name}%"),
        ).order_by(
            models.TestCase.id.desc()
        ).offset(size * (page - 1)).limit(size)
    )
    return result.all()
