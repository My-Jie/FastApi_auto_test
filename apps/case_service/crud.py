#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/20-21:59
"""

import datetime
from tools import rep_value, rep_url
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
from apps.case_service import models, schemas


async def create_test_case(db: Session, case_name: str, mode: str, temp_id: int):
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
    db.commit()
    db.refresh(db_case)
    return db_case


async def update_test_case(db: Session, case_id: int, case_count: int = None):
    """
    更新测试信息
    :param db:
    :param case_id:
    :param case_count:
    :return:
    """
    db_temp = db.query(models.TestCase).filter(models.TestCase.id == case_id).first()
    if db_temp:
        db_temp.case_count = case_count
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def create_test_case_data(db: Session, data: schemas.TestCaseDataIn, case_id: int):
    """
    创建测试数据集
    :param db:
    :param data:
    :param case_id:
    :return:
    """
    db_data = models.TestCaseData(**data.dict(), case_id=case_id)
    db.add(db_data)
    # db.commit()
    # db.refresh(db_data)
    return db_data


async def create_test_case_data_add(db: Session, data: schemas.TestCaseDataInTwo):
    """
    创建测试数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TestCaseData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def del_test_case_data(db: Session, case_id: int, number: int = None):
    """
    删除测试数据，不删除用例
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    if number:
        db.query(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number
        ).delete()
        db.commit()
        return

    db.query(models.TestCaseData).filter(models.TestCaseData.case_id == case_id).delete()
    db.commit()


async def get_case_info(
        db: Session,
        case_name: str = None,
        case_id: int = None,
        all_: bool = False,
        page: int = 1,
        size: int = 10
):
    """
    按用例名称查询数据
    :param db:
    :param case_name:
    :param case_id:
    :param all_:
    :param page:
    :param size::
    :return:
    """
    if case_id is not None:
        return db.query(models.TestCase).filter(models.TestCase.id == case_id).order_by(models.TestCase.id.desc()).all()

    if case_name:
        return db.query(models.TestCase).filter(
            models.TestCase.case_name.like(f"%{case_name}%"),
        ).order_by(
            models.TestCase.id.desc()
        ).offset(size * (page - 1)).limit(size)
    if all_:
        return db.query(models.TestCase).order_by(models.TestCase.id.desc()).all()

    if page and size:
        return db.query(models.TestCase).order_by(models.TestCase.id.desc()).offset(size * (page - 1)).limit(size)


async def get_case_data(db: Session, case_id: int, number: int = None):
    """
    查询测试用例数据
    :param db:
    :param case_id:
    :param number:
    :return:
    """

    if number:
        return db.query(models.TestCaseData).filter(
            models.TestCaseData.case_id == case_id,
            models.TestCaseData.number == number
        ).order_by(
            models.TestCaseData.number
        ).all()
    else:
        return db.query(models.TestCaseData).filter(models.TestCaseData.case_id == case_id).order_by(
            models.TestCaseData.number
        ).all()


async def set_case_info(
        db: Session,
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
    db_temp = db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number == number,
    ).first()

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

        db.commit()
        db.refresh(db_temp)
        return db_temp


async def set_case_description(db: Session, case_id: int, number: int, description: str):
    """
    设置用例描述信息
    :param db:
    :param case_id:
    :param number:
    :param description:
    :return:
    """
    db_temp = db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number == number,
    ).first()

    if db_temp:
        db_temp.description = description
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def set_case_data(
        db: Session,
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
    db_temp = db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number == number,
    ).first()

    if type_ == 'data':
        new_json = rep_value(json_data=db_temp.data, old_str=old_data, new_str=new_data)
        db_temp.data = new_json
        flag_modified(db_temp, "data")
        db.commit()
        db.refresh(db_temp)
        return db_temp
    elif type_ == 'params':
        new_json = rep_value(json_data=db_temp.params, old_str=old_data, new_str=new_data)
        db_temp.params = new_json
        flag_modified(db_temp, "params")
        db.commit()
        db.refresh(db_temp)
        return db_temp
    elif type_ == 'headers':
        new_json = rep_value(json_data=db_temp.headers, old_str=old_data, new_str=new_data)
        db_temp.headers = new_json
        flag_modified(db_temp, "headers")
        db.commit()
        db.refresh(db_temp)
        return db_temp
    else:
        new_url = rep_url(url=db_temp.path, old_str=old_data, new_str=new_data)
        db_temp.path = new_url
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def del_case_data(db: Session, case_id: int):
    """
    删除测试数据
    :param db:
    :param case_id:
    :return:
    """
    db.query(models.TestCase).filter(models.TestCase.id == case_id).delete()
    db.query(models.TestCaseData).filter(models.TestCaseData.case_id == case_id).delete()
    db.commit()


async def get_case(db: Session, temp_id: int):
    """
    按模板查用例
    :param db:
    :param temp_id:
    :return:
    """
    return db.query(models.TestCase).filter(models.TestCase.temp_id == temp_id).all()


async def get_case_ids(db: Session, temp_id: int):
    """
    按模板查用例id
    :param db:
    :param temp_id:
    :return:
    """
    return db.query(models.TestCase.id).filter(models.TestCase.temp_id == temp_id).order_by(models.TestCase.id).all()


async def get_urls(db: Session, url: str):
    """
    模糊查询url
    :param db:
    :param url:
    :return:
    """
    return db.query(models.TestCaseData).filter(models.TestCaseData.path.like(f"{url}%")).order_by(
        models.TestCaseData.number
    ).all()


async def update_urls(db: Session, old_url: str, new_url: str):
    """
    按url查询数据
    :param db:
    :param old_url:
    :param new_url:
    :return:
    """
    if not await get_urls(db=db, url=old_url):
        return None

    db_info = db.query(models.TestCaseData).filter(models.TestCaseData.path.like(f"{old_url}%")).order_by(
        models.TestCaseData.number
    ).all()

    url_info = []
    for info in db_info:
        info.path = new_url
        db.commit()
        db.refresh(info)
        url_info.append(info)
    return url_info


async def get_api_info(db: Session, case_id: int, number: int):
    """
    查询用例api信息
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    return db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number == number
    ).first()


async def update_api_info(db: Session, api_info: schemas.TestCaseDataOut1):
    """
    修改用例api信息
    :param db:
    :param api_info:
    :return:
    """
    if not await get_api_info(db=db, case_id=api_info.case_id, number=api_info.number):
        return False

    db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == api_info.case_id,
        models.TestCaseData.number == api_info.number
    ).update(api_info.dict())
    db.commit()
    return True


async def update_api_number(db: Session, case_id: int, id_: int, new_number: int):
    """
    更新用例的number
    :param db:
    :param case_id:
    :param id_:
    :param new_number:
    :return:
    """
    db_temp = db.query(models.TestCaseData).filter(
        models.TestCaseData.id == id_,
        models.TestCaseData.case_id == case_id,
    ).first()

    if db_temp:
        db_temp.number = new_number
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def put_case_name(db: Session, case_id: int, new_name: str):
    """
    更新用例名称
    :param db:
    :param case_id:
    :param new_name:
    :return:
    """
    db_temp = None

    if case_id:
        db_temp = db.query(models.TestCase).filter(models.TestCase.id == case_id).first()

    if db_temp:
        db_temp.case_name = new_name
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def get_case_numbers(db: Session, case_id: int, number: int):
    """
    查询某个number后的用例数据
    :param db:
    :param case_id:
    :param number:
    :return:
    """
    return db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number >= number
    ).order_by(
        models.TestCaseData.number
    ).order_by(
        models.TestCaseData.id.desc()
    ).all()


async def get_count(db: Session, case_name: str = None, today: bool = None):
    """
    记数查询
    :param db:
    :param case_name:
    :param today:
    :return:
    """
    if case_name:
        return db.query(func.count(models.TestCase.id)).filter(
            models.TestCase.case_name.like(f"%{case_name}%")
        ).scalar()

    if today:
        return db.query(func.count(models.TestCase.id)).filter(
            models.TestCase.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.TestCase.id)).scalar()


async def get_api_count(db: Session, today: bool = None):
    """
    记数查询
    :param db:
    :param today:
    :return:
    """
    if today:
        return db.query(func.count(models.TestCaseData.id)).filter(
            models.TestCaseData.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.TestCaseData.id)).scalar()


async def get_case_detail(db: Session, detail_id: int, ):
    """
    查询模板数据
    :param db:
    :param detail_id:
    :return:
    """
    return db.query(models.TestCaseData).filter(
        models.TestCaseData.id == detail_id,
    ).first()


async def update_case_path(db: Session, detail_id: int, new_path: str):
    """
    更新用例path
    :param db:
    :param detail_id:
    :param new_path:
    :return:
    """
    db_temp = db.query(models.TestCaseData).filter(
        models.TestCaseData.id == detail_id,
    ).first()
    if db_temp:
        db_temp.path = new_path
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def get_case_info_to_number(
        db: Session,
        case_id: int,
        numbers: (tuple, list),
):
    return db.query(models.TestCaseData).filter(
        models.TestCaseData.case_id == case_id,
        models.TestCaseData.number.in_(numbers)
    ).all()
