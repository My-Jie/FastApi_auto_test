#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/4-15:24
"""

from sqlalchemy.orm import Session
from apps.api_pool import models
from apps.api_pool import schemas


async def create_api_project(db: Session, data: schemas.YApi):
    """
    按项目创建项目列表
    :param db:
    :param data:
    :return:
    """
    db_data = models.YAoiProject(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def update_api_project(db: Session, yai_id: int, api_count: int):
    """
    更新用例池数据
    :param db:
    :param yai_id:
    :param api_count:
    :return:
    """
    db_temp = db.query(models.YAoiProject).filter(models.YAoiProject.id == yai_id).first()
    if db_temp:
        db_temp.api_count = api_count
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def create_api_pool(db: Session, data: schemas.YApiData):
    """
    创建用例池
    :param db:
    :param data:
    :return:
    """
    db_data = models.YApiPool(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def get_project_info(db: Session, group_name: str = None, project_name: str = None, project_id: int = None):
    """
    按项目名称查询数据
    :param db:
    :param group_name:
    :param project_name:
    :param project_id:
    :return:
    """
    if group_name:
        return db.query(models.YAoiProject).filter(models.YAoiProject.group_name == group_name).all()

    if project_name:
        return db.query(models.YAoiProject).filter(models.YAoiProject.project_name == project_name).all()

    if project_id:
        return db.query(models.YAoiProject).filter(models.YAoiProject.project_id == project_id).all()

    return db.query(models.YAoiProject).all()


async def get_api_info(db: Session, project_name: str = None, project_id: int = None):
    """
    获取项目下的详情数据
    :param db:
    :param project_name:
    :param project_id:
    :return:
    """
    if project_name:
        return db.query(models.YApiPool).join(
            models.YAoiProject, models.YAoiProject.project_id == models.YApiPool.project_id).filter(
            models.YAoiProject.project_name == project_name
        ).all()

    if project_id:
        return db.query(models.YApiPool).join(
            models.YAoiProject, models.YAoiProject.project_id == models.YApiPool.project_id).filter(
            models.YAoiProject.project_id == project_id
        ).all()


async def get_api(db: Session, api_id: int = None, title: str = None):
    """
    获取单个接口数据
    :param db:
    :param api_id:
    :param title:
    :return:
    """
    if api_id:
        return db.query(models.YApiPool).filter(models.YApiPool.api_id == api_id).first()
    if title:
        return db.query(models.YApiPool).filter(models.YApiPool.title == title).first()


async def del_api_info(db: Session, api_id: int):
    """
    删除单个接口的数据
    :param db:
    :param api_id:
    :return:
    """
    db.query(models.YApiPool).filter(models.YApiPool.api_id == api_id).delete()


async def del_project_all(db: Session):
    """
    删除所有YApi接口数据
    :param db:
    :return:
    """
    db.query(models.YAoiProject).delete()
    db.commit()


async def del_api_all(db: Session):
    """
    删除所有api数据
    :param db:
    :return:
    """
    db.query(models.YApiPool).delete()
    db.commit()


async def del_project_api_info(db: Session, project_id: int):
    """
    按单个项目删除所有api
    :param db:
    :param project_id:
    :return:
    """
    db.query(models.YApiPool).filter(models.YApiPool.project_id == project_id).delete()
    db.commit()
