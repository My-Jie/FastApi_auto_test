#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/7/27-16:06
"""

from sqlalchemy.orm import Session
from apps.setting_bind import models, schemas
from sqlalchemy.orm.attributes import flag_modified


async def create_setting(db: Session, setting: schemas.SettingSetIn):
    db_info = models.SettingSet(**setting.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_setting(db: Session, id_: int = None, name: str = None):
    if id_:
        return db.query(models.SettingSet).filter(models.SettingSet.id == id_).all()

    if name:
        return db.query(models.SettingSet).filter(models.SettingSet.name == name).all()

    return db.query(models.SettingSet).all()


async def update_setting_name(db: Session, id_: int, name: str):
    db_info = db.query(models.SettingSet).filter(models.SettingSet.id == id_).first()
    if db_info:
        db_info.name = name
        db.commit()
        db.refresh(db_info)
        return db_info


async def update_setting_bind(
        db: Session, id_: int,
        bind: bool,
        api_case: int = None,
        ui_case: int = None,
        host: int = None,
        customize: int = None,
        db_: int = None,
):
    db_temp = db.query(models.SettingSet).filter(
        models.SettingSet.id == id_,
    ).first()

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

        db.commit()
        db.refresh(db_temp)
        return db_temp


async def del_setting(db: Session, id_: int):
    db.query(models.SettingSet).filter(
        models.SettingSet.id == id_,
    ).delete()
    db.commit()
