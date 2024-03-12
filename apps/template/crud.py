#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2022/8/8-10:19
"""

import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from apps.template import models, schemas
from apps.case_service import models as case_models
from apps.api_report import models as report_models


async def create_template(db: Session, temp_name: str, project_name: int):
    """
    创建模板信息
    :param db:
    :param temp_name:
    :param project_name:
    :return:
    """
    db_temp = models.Template(temp_name=temp_name, project_name=project_name)
    db.add(db_temp)
    db.commit()
    db.refresh(db_temp)
    return db_temp


async def update_template(db: Session, temp_id: int, api_count: int = None):
    """
    更新模板信息
    :param db:
    :param temp_id:
    :param api_count:
    :return:
    """
    db_temp = db.query(models.Template).filter(models.Template.id == temp_id).first()
    if db_temp:
        db_temp.api_count = api_count
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def create_template_data(db: Session, data: schemas.TemplateDataIn, temp_id: int):
    """
    创建模板数据集
    :param db:
    :param data:
    :param temp_id:
    :return:
    """
    db_data = models.TemplateData(**data.dict(), temp_id=temp_id)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def create_template_data_add(db: Session, data: schemas.TemplateDataInTwo):
    """
    创建模板数据集
    :param db:
    :param data:
    :return:
    """
    db_data = models.TemplateData(**data.dict())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


async def update_template_data(db: Session, temp_id: int, id_: int, new_number: int, old_number: int = None):
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
        db_temp = db.query(models.TemplateData).filter(
            models.TemplateData.id == id_,
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number == old_number
        ).first()
    else:
        db_temp = db.query(models.TemplateData).filter(
            models.TemplateData.id == id_,
            models.TemplateData.temp_id == temp_id,
        ).first()
    if db_temp:
        db_temp.number = new_number
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def get_temp_name(
        db: Session,
        temp_name: str = None,
        temp_id: int = None,
        like: bool = False,
        page: int = 1,
        size: int = 10
):
    """
    按模板名称查询数据
    :param db:
    :param temp_name:
    :param temp_id:
    :param like:
    :param page:
    :param size:
    :return:
    """
    if temp_id is not None:
        return db.query(models.Template).filter(models.Template.id == temp_id).order_by(models.Template.id.desc()).all()

    if temp_name:
        if like:
            return db.query(models.Template).filter(
                models.Template.temp_name.like(f"%{temp_name}%"),
            ).order_by(
                models.Template.id.desc()
            ).offset(size * (page - 1)).limit(size)
        else:
            return db.query(models.Template).filter(models.Template.temp_name == temp_name).order_by(
                models.Template.id.desc()
            ).all()

    return db.query(models.Template).order_by(models.Template.id.desc()).offset(size * (page - 1)).limit(size)


async def get_temp_case_info(db: Session, temp_id: int, outline: bool):
    """
    查询模板下有多少条用例
    :param db:
    :param temp_id:
    :param outline:
    :return:
    """
    db_case = db.query(case_models.TestCase).filter(case_models.TestCase.temp_id == temp_id).order_by(
        case_models.TestCase.id
    ).all()
    case_info = []
    for case in db_case:
        if outline is False:
            report = db.query(report_models.ApiReportList).filter(
                report_models.ApiReportList.case_id == case.id,
            ).order_by(
                report_models.ApiReportList.id.desc()
            ).first()
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


async def get_template_data(db: Session, temp_name: str = None, temp_id: int = None, numbers: list = None):
    """
    查询模板数据
    :param db:
    :param temp_name:
    :param temp_id:
    :param numbers:
    :return:
    """
    if temp_name:
        db_temp = db.query(models.Template).filter(models.Template.temp_name == temp_name).first()
        if db_temp:
            return db.query(models.TemplateData).filter(models.TemplateData.temp_id == db_temp.id).order_by(
                models.TemplateData.number
            ).all()

    if temp_id and numbers:
        return db.query(models.TemplateData).filter(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.number.in_(numbers),
        ).order_by(
            models.TemplateData.number
        ).all()

    if temp_id:
        return db.query(models.TemplateData).filter(models.TemplateData.temp_id == temp_id).order_by(
            models.TemplateData.number
        ).all()


async def get_tempdata_detail(db: Session, detail_id: int, ):
    """
    查询模板数据
    :param db:
    :param detail_id:
    :return:
    """
    return db.query(models.TemplateData).filter(
        models.TemplateData.id == detail_id,
    ).first()


async def get_temp_host(db: Session, temp_id: int):
    """
    查询模板数据
    :param db:
    :param temp_id:
    :return:
    """
    return db.query(models.TemplateData.host).filter(models.TemplateData.temp_id == temp_id).order_by(
        models.TemplateData.number
    ).all()


async def put_temp_name(db: Session, new_name: str, temp_id: int = None, old_name: str = None):
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
        db_temp = db.query(models.Template).filter(models.Template.id == temp_id).first()

    if old_name:
        db_temp = db.query(models.Template).filter(models.Template.temp_name == old_name).first()

    if db_temp:
        db_temp.temp_name = new_name
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def put_description(db: Session, new_description: str, api_id: int):
    """
    更新模板描述
    :param db:
    :param new_description:
    :param api_id:
    :return:
    """
    db_temp = db.query(models.TemplateData).filter(models.TemplateData.id == api_id).first()
    if db_temp:
        db_temp.description = new_description
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def del_template_data_all(db: Session, temp_name: str = None, temp_id: int = None):
    """
    删除所有模板数据
    :param db:
    :param temp_name:
    :param temp_id:
    :return:
    """
    db_temp = None
    if temp_name:
        db_temp = db.query(models.Template).filter(models.Template.temp_name == temp_name).first()

    if temp_id:
        db_temp = db.query(models.Template).filter(models.Template.id == temp_id).first()

    if db_temp:
        db.query(models.TemplateData).filter(models.TemplateData.temp_id == db_temp.id).delete()
        db.query(models.Template).filter(models.Template.id == db_temp.id).delete()
        db.commit()
        return db_temp


async def del_template_data(db: Session, temp_id: int, number: int):
    """
    删除部分数据
    :param db:
    :param temp_id:
    :param number:
    :return:
    """
    db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == temp_id,
        models.TemplateData.number == number
    ).delete()


async def get_all_temp_name(db: Session, temp_ids):
    """
    获取所有的模板名称
    :param db:
    :param temp_ids:
    :return:
    """
    db_temp = db.query(
        models.Template.temp_name
    ).filter(
        models.Template.id.in_(temp_ids)
    ).all()
    return db_temp


async def get_new_temp_info(db: Session, temp_id: int, number: int, method: str):
    """

    :param db:
    :param temp_id:
    :param number:
    :param method:
    :return:
    """
    return db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == temp_id,
        models.TemplateData.number == number,
        models.TemplateData.method == method
    ).order_by(
        models.TemplateData.number
    ).first()


async def get_temp_all(db: Session):
    """
    查询所有模板数据
    :param db:
    :return:
    """
    return db.query(
        models.TemplateData.temp_id,
        models.TemplateData.number,
        models.TemplateData.method,
        models.TemplateData.path
    ).order_by(
        models.TemplateData.id
    ).all()


async def update_api_info(db: Session, api_info: schemas.TemplateDataInTwo):
    """
    修改用例api信息
    :param db:
    :param api_info:
    :return:
    """
    if not await get_template_data(db=db, temp_id=api_info.temp_id, numbers=[api_info.number]):
        return False

    db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == api_info.temp_id,
        models.TemplateData.number == api_info.number
    ).update({
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
    db.commit()
    return True


async def get_temp_numbers(db: Session, temp_id: int, number: int):
    """
    查询某个number后的模板数据
    :param db:
    :param temp_id:
    :param number:
    :return:
    """
    return db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == temp_id,
        models.TemplateData.number >= number
    ).order_by(
        models.TemplateData.number.desc()
    ).all()


async def get_count(db: Session, temp_name: str = None, today: bool = None):
    """
    记数查询
    :param db:
    :param temp_name:
    :param today:
    :return:
    """
    if temp_name:
        return db.query(func.count(models.Template.id)).filter(
            models.Template.temp_name.like(f"%{temp_name}%")
        ).scalar()

    if today:
        return db.query(func.count(models.Template.id)).filter(
            models.Template.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.Template.id)).scalar()


async def get_api_count(db: Session, today: bool = None):
    """
    记数查询
    :param db:
    :param today:
    :return:
    """
    if today:
        return db.query(func.count(models.TemplateData.id)).filter(
            models.TemplateData.created_at >= datetime.datetime.now().date()
        ).scalar()

    return db.query(func.count(models.TemplateData.id)).scalar()


async def save_temp_info(
        db: Session,
        temp_id: int,
        number: int,
        params: dict = None,
        data: dict = None,
        headers: dict = None,
):
    """
    更新用例的数据
    """
    db_temp = db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == temp_id,
        models.TemplateData.number == number,
    ).first()

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

        db.commit()
        db.refresh(db_temp)
        return db_temp


async def save_path_info(db: Session, temp_id: int, number: int, api_path: dict):
    """
    更新用例的path
    """
    db_temp = db.query(models.TemplateData).filter(
        models.TemplateData.temp_id == temp_id,
        models.TemplateData.number == number,
    ).first()

    if db_temp:
        db_temp.method = api_path['method']
        db_temp.path = api_path['path']
        db_temp.code = api_path['code']
        db.commit()
        db.refresh(db_temp)
        return db_temp


async def sync_temp(
        db: Session,
        number: int,
        method: str,
        path: str,
        data_type: str,
        temp_id: int = None,
):
    """
    按method+path查询模板的数据
    :param db:
    :param number:
    :param method:
    :param path:
    :param data_type:
    :param temp_id: 传了temp_id就查询当前模板的数据， 没有传就查询所有
    :return:
    """
    if temp_id:
        db_temp = db.query(models.TemplateData).filter(
            models.TemplateData.temp_id == temp_id,
            models.TemplateData.method == method,
            models.TemplateData.path == path,
        ).all()
    else:
        db_temp = db.query(models.TemplateData).filter(
            models.TemplateData.method == method,
            models.TemplateData.path == path,
        ).all()

    if data_type == 'params':
        return [
            {
                'temp_id': x.temp_id,
                'number': x.number,
                'method': x.method,
                'path': x.path,
                'data': x.params,
                'description': x.description,
                'active_name': '1',
            } for x in db_temp if any([
                x.temp_id == temp_id and x.number != number,
                x.temp_id != temp_id and x.number == number
            ])
        ]

    if data_type == 'data':
        return [
            {
                'temp_id': x.temp_id,
                'number': x.number,
                'method': x.method,
                'path': x.path,
                'data': x.data,
                'description': x.description,
                'active_name': '1',
            } for x in db_temp if any([
                x.temp_id == temp_id and x.number != number,
                x.temp_id != temp_id and x.number == number
            ])
        ]

    if data_type == 'headers':
        return [
            {
                'temp_id': x.temp_id,
                'number': x.number,
                'method': x.method,
                'path': x.path,
                'data': x.headers,
                'description': x.description,
                'active_name': '1',
            } for x in db_temp if any([
                x.temp_id == temp_id and x.number != number,
                x.temp_id != temp_id and x.number == number
            ])
        ]
