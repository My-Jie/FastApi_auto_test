#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/6/9-16:30
"""

from sqlalchemy import func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from apps.case_ui import models, schemas
from typing import List


async def create_playwright(db: AsyncSession, data: schemas.PlaywrightIn, rows: int):
    """
    创建模板信息
    :param db:
    :param data:
    :param rows:
    :return:
    """
    db_temp = models.PlaywrightTemp(**data.dict(), rows=rows)
    db.add(db_temp)
    await db.commit()
    await db.refresh(db_temp)
    return db_temp


async def get_playwright(
        db: AsyncSession,
        temp_id: int = None,
        temp_name: str = None,
        like: bool = False,
        page: int = 1,
        size: int = 10
):
    """
    查询列表
    :param db:
    :param temp_id:
    :param temp_name:
    :param like:
    :param page:
    :param size:
    :return:
    """
    if temp_id is not None:
        result = await db.execute(
            select(models.PlaywrightTemp).where(models.PlaywrightTemp.id == temp_id)
        )
        return result.scalars().all()

    if temp_name:
        if like:
            result = await db.execute(
                select(models.PlaywrightTemp).where(
                    models.PlaywrightTemp.temp_name.like(f"%{temp_name}%")
                ).order_by(
                    models.PlaywrightTemp.id.desc()
                ).offset(size * (page - 1)).limit(size)
            )
            return result.scalars().all()

        result = await db.execute(
            select(models.PlaywrightTemp).where(
                models.PlaywrightTemp.temp_name == temp_name
            )
        )
        return result.scalars().all()

    result = await db.execute(
        select(models.PlaywrightTemp).order_by(
            models.PlaywrightTemp.id.desc()
        ).offset(size * (page - 1)).limit(size)
    )
    return result.scalars().all()


async def get_playwright_data(db: AsyncSession, temp_id: int):
    """
    获取文本详情
    :param db:
    :param temp_id:
    :return:
    """
    result = await db.execute(
        select(models.PlaywrightTemp).where(models.PlaywrightTemp.id == temp_id)
    )
    return result.scalars().first()


async def update_playwright(db: AsyncSession, temp_id: int, project_name: str, temp_name: str, rows: int, text: str):
    """
    更新模板信息
    """
    result = await db.execute(
        select(models.PlaywrightTemp).where(models.PlaywrightTemp.id == temp_id)
    )
    db_temp = result.scalars().first()
    if db_temp:
        db_temp.project_name = project_name
        db_temp.temp_name = temp_name
        db_temp.rows = rows
        db_temp.text = text
        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def del_template_data(db: AsyncSession, temp_id: int):
    """
    删除部分数据
    :param db:
    :param temp_id:
    :return:
    """
    await db.execute(
        delete(models.PlaywrightCaseDate).where(
            models.PlaywrightCaseDate.id == temp_id
        )
    )
    await db.commit()


async def create_play_case_data(db: AsyncSession, data: schemas.PlaywrightDataIn):
    """
    获取测试数据
    :param db:
    :param data:
    :return:
    """
    db_temp = models.PlaywrightCaseDate(**data.dict())
    db.add(db_temp)
    await db.commit()
    await db.refresh(db_temp)
    return db_temp


async def get_play_case_data(db: AsyncSession, case_id: int = None, temp_id: int = None, case_ids: list = None):
    """
    获取测试用例的数据
    :param db:
    :param case_id:
    :param case_ids:
    :param temp_id:
    :return:
    """
    if case_ids and temp_id:
        result = await db.execute(
            select(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.temp_id == temp_id,
                models.PlaywrightCaseDate.id.in_(case_ids)
            )
        )
        return result.scalars().all()

    if case_id and temp_id:
        result = await db.execute(
            select(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.id == case_id,
                models.PlaywrightCaseDate.temp_id == temp_id
            )
        )
        return result.scalars().all()

    if temp_id:
        result = await db.execute(
            select(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.temp_id == temp_id
            )
        )
        return result.scalars().all()

    result = await db.execute(
        select(models.PlaywrightCaseDate)
    )
    return result.scalars().all()


async def del_play_case_data(db: AsyncSession, case_id: int = None, temp_id: int = None, case_ids: List[int] = None):
    """
    删除测试数据集
    :param db:
    :param case_id:
    :param temp_id:
    :param case_ids:
    :return:
    """
    if case_ids:
        await db.execute(
            delete(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.temp_id == temp_id,
                models.PlaywrightCaseDate.id.in_(case_ids)
            )
        )
        await db.commit()
        return

    if case_id:
        await db.execute(
            delete(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.id == case_id,
            )
        )
        await db.commit()
        return

    if temp_id:
        await db.execute(
            delete(models.PlaywrightCaseDate).where(
                models.PlaywrightCaseDate.temp_id == temp_id
            )
        )
        await db.commit()
        return


async def update_ui_temp_order(db: AsyncSession, temp_id: int, is_fail: bool, i: int = 1):
    """
    更新用例次数
    :param db:
    :param temp_id:
    :param is_fail:
    :param i:
    :return:
    """
    result = await db.execute(
        select(models.PlaywrightTemp).where(models.PlaywrightTemp.id == temp_id)
    )
    db_case = result.scalars().first()
    db_case.run_order = db_case.run_order + i
    if is_fail:
        db_case.fail = db_case.fail + 1
    else:
        db_case.success = db_case.success + 1
    await db.commit()
    await db.refresh(db_case)
    return db_case


async def get_count(db: AsyncSession, temp_name: str = None):
    """
    记数查询
    :param db:
    :param temp_name:
    :return:
    """
    if temp_name:
        result = await db.execute(
            select(func.count(models.PlaywrightTemp.id)).where(
                models.PlaywrightTemp.temp_name.like(f"%{temp_name}%")
            )
        )
        return result.scalar()

    result = await db.execute(
        select(func.count(models.PlaywrightTemp.id))
    )
    return result.scalar()


async def get_ddt_count(db: AsyncSession):
    """
    记数查询
    :param db:
    :return:
    """
    result = await db.execute(
        select(func.count(models.PlaywrightCaseDate.temp_id.distinct()))
    )
    return result.scalar()
