#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/7/27-16:06
"""

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from apps.setting_bind import models, schemas
from sqlalchemy.orm.attributes import flag_modified


async def create_setting(db: AsyncSession, setting: schemas.SettingSetIn):
    db_info = models.SettingSet(**setting.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_setting(db: AsyncSession, id_: int = None, name: str = None):
    if id_:
        result = await db.execute(
            select(models.SettingSet).filter(models.SettingSet.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.SettingSet).filter(models.SettingSet.name == name)
        )
        return result.scalars().all()

    result = await db.execute(select(models.SettingSet))
    return result.scalars().all()


async def update_setting_name(db: AsyncSession, id_: int, name: str):
    result = await db.execute(
        select(models.SettingSet).filter(models.SettingSet.id == id_)
    )
    db_info = result.scalars().first()
    if db_info:
        db_info.name = name
        await db.commit()
        await db.refresh(db_info)
        return db_info


async def update_setting_bind(
        db: AsyncSession, id_: int,
        bind: bool,
        api_case: int = None,
        ui_case: int = None,
        host: int = None,
        customize: int = None,
        db_: int = None,
):
    result = await db.execute(
        select(models.SettingSet).filter(models.SettingSet.id == id_)
    )
    db_temp = result.scalars().first()

    if db_temp:
        if api_case is not None:
            db_temp.api_case_ids.append(api_case) if bind else db_temp.api_case_ids.remove(api_case)
            flag_modified(db_temp, "api_case_ids")
        if ui_case is not None:
            db_temp.ui_case_ids.append(ui_case) if bind else db_temp.ui_case_ids.remove(ui_case)
            flag_modified(db_temp, "ui_case_ids")
        if host is not None:
            db_temp.host_ids.append(host) if bind else db_temp.host_ids.remove(host)
            flag_modified(db_temp, "host_ids")
        if customize is not None:
            db_temp.customize_ids.append(customize) if bind else db_temp.customize_ids.remove(customize)
            flag_modified(db_temp, "customize_ids")
        if db_ is not None:
            db_temp.db_ids.append(db_) if bind else db_temp.db_ids.remove(db_)
            flag_modified(db_temp, "db_ids")

        await db.commit()
        await db.refresh(db_temp)
        return db_temp


async def del_setting(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.SettingSet).where(models.SettingSet.id == id_)
    )
    await db.commit()
