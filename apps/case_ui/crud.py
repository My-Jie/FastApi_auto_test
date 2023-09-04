#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/6/9-16:30
"""

from sqlalchemy import func
from sqlalchemy.orm import Session
from apps.case_ui import models, schemas


async def create_playwright(db: Session, data: schemas.PlaywrightIn, rows: int):
    """
    创建模板信息
    :param db:
    :param data:
    :param rows:
    :return:
    """
    db_temp = models.PlaywrightTemp(**data.dict(), rows=rows)
    db.add(db_temp)
    db.commit()
    db.refresh(db_temp)
    return db_temp


async def get_playwright(
        db: Session,
        temp_id: int = None,
        temp_name: str = None,
        like: bool = False,
        page: int = 1,
        size: int = 10
):
    """
    查询内容
    :param db:
    :param temp_id:
    :param temp_name:
    :param like:
    :param page:
    :param size:
    :return:
    """
    if temp_id is not None:
        return db.query(models.PlaywrightTemp).filter(
            models.PlaywrightTemp.id == temp_id
        ).all()

    if temp_name:
        if like:
            return db.query(models.PlaywrightTemp).filter(
                models.PlaywrightTemp.temp_name.like(f"%{temp_name}%"),
            ).order_by(
                models.PlaywrightTemp.id.desc()
            ).offset(size * (page - 1)).limit(size)

        return db.query(models.PlaywrightTemp).filter(
            models.PlaywrightTemp.temp_name == temp_name
        ).all()

    return db.query(models.PlaywrightTemp).order_by(
        models.PlaywrightTemp.id.desc()
    ).offset(size * (page - 1)).limit(size)


async def update_playwright(db: Session, temp_id: int, project_name: str, temp_name: str, rows: int, text: str):
    """
    更新模板信息
    """
    db_temp = db.query(models.PlaywrightTemp).filter(models.PlaywrightTemp.id == temp_id).first()
    if db_temp:
        db_temp.project_name = project_name
        db_temp.temp_name = temp_name
        db_temp.rows = rows
        db_temp.text = text
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def del_template_data(db: Session, temp_id: int):
    """
    删除部分数据
    :param db:
    :param temp_id:
    :return:
    """
    db.query(models.PlaywrightTemp).filter(
        models.PlaywrightTemp.id == temp_id,
    ).delete()
    db.commit()


async def create_play_case_data(db: Session, data: schemas.PlaywrightDataIn):
    """
    获取测试数据
    :param db:
    :param data:
    :return:
    """
    db_temp = models.PlaywrightCaseDate(**data.dict())
    db.add(db_temp)
    db.commit()
    db.refresh(db_temp)
    return db_temp


async def get_play_case_data(db: Session, case_id: int = None, temp_id: int = None, case_ids: list = None):
    """
    获取测试用例的数据
    :param db:
    :param case_id:
    :param case_ids:
    :param temp_id:
    :return:
    """
    if case_ids and temp_id:
        return db.query(models.PlaywrightCaseDate).filter(
            models.PlaywrightCaseDate.temp_id == temp_id,
            models.PlaywrightCaseDate.id.in_(case_ids)
        ).all()

    if case_id and temp_id:
        return db.query(models.PlaywrightCaseDate).filter(
            models.PlaywrightCaseDate.id == case_id,
            models.PlaywrightCaseDate.temp_id == temp_id
        ).all()

    if temp_id:
        return db.query(models.PlaywrightCaseDate).filter(
            models.PlaywrightCaseDate.temp_id == temp_id
        ).all()

    return db.query(models.PlaywrightCaseDate).all()


async def del_play_case_data(db: Session, case_id: int = None, temp_id: int = None):
    """
    删除测试呼叫
    :param db:
    :param case_id:
    :param temp_id:
    :return:
    """
    if case_id:
        db.query(models.PlaywrightCaseDate).filter(
            models.PlaywrightCaseDate.id == case_id,
        ).delete()
        db.commit()
        return

    if temp_id:
        db.query(models.PlaywrightCaseDate).filter(
            models.PlaywrightCaseDate.temp_id == temp_id,
        ).delete()
        db.commit()
        return


async def update_ui_temp_order(db: Session, temp_id: int, is_fail: bool):
    """
    更新用例次数
    :param db:
    :param temp_id:
    :param is_fail:
    :return:
    """
    db_case = db.query(models.PlaywrightTemp).filter(models.PlaywrightTemp.id == temp_id).first()
    db_case.run_order = db_case.run_order + 1
    if is_fail:
        db_case.fail = db_case.fail + 1
    else:
        db_case.success = db_case.success + 1
    db.commit()
    db.refresh(db_case)
    return db_case


async def get_count(db: Session, temp_name: str = None):
    """
    记数查询
    :param db:
    :param temp_name:
    :return:
    """
    if temp_name:
        return db.query(func.count(models.PlaywrightTemp.id)).filter(
            models.PlaywrightTemp.temp_name.like(f"%{temp_name}%")
        ).scalar()

    return db.query(func.count(models.PlaywrightTemp.id)).scalar()


async def get_ddt_count(db: Session):
    """
    记数查询
    :param db:
    :return:
    """
    return db.query(func.count(models.PlaywrightCaseDate.temp_id.distinct())).scalar()
