#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/4/16-14:42
"""

from sqlalchemy.orm import Session
from apps.whole_conf import models, schemas

"""
域名列表的crud
"""


async def create_host(db: Session, conf_host: schemas.ConfHostIn):
    db_info = models.ConfHost(**conf_host.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_host(db: Session, id_: int = None, name: str = None, ids: list = None):
    if id_:
        return db.query(models.ConfHost).filter(models.ConfHost.id == id_).all()

    if name:
        return db.query(models.ConfHost).filter(models.ConfHost.name == name).all()

    if ids:
        return db.query(models.ConfHost).filter(models.ConfHost.id.in_(ids)).all()

    return db.query(models.ConfHost).all()


async def update_host(db: Session, id_: int, conf_host: schemas.ConfHostIn):
    db.query(models.ConfHost).filter(
        models.ConfHost.id == id_
    ).update(conf_host.dict())
    db.commit()


async def del_host(db: Session, id_: int):
    db.query(models.ConfHost).filter(
        models.ConfHost.id == id_,
    ).delete()
    db.commit()


"""
项目列表的crud
"""


async def create_project(db: Session, conf_project: schemas.ConfProjectIn):
    db_info = models.ConfProject(**conf_project.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_project(db: Session, id_: int = None, name: str = None):
    if id_:
        return db.query(models.ConfProject).filter(models.ConfProject.id == id_).all()

    if name:
        return db.query(models.ConfProject).filter(models.ConfProject.name == name).all()

    return db.query(models.ConfProject).all()


async def get_project_code(db: Session, id_: int = None):
    db_info = db.query(models.ConfProject.code).filter(models.ConfProject.id == id_).first()
    if db_info:
        return db_info[0]


async def update_project(db: Session, id_: int, conf_project: schemas.ConfProjectIn):
    db.query(models.ConfProject).filter(
        models.ConfProject.id == id_
    ).update(conf_project.dict())
    db.commit()


async def del_project(db: Session, id_: int):
    db.query(models.ConfProject).filter(
        models.ConfProject.id == id_,
    ).delete()
    db.commit()


"""
数据库列表的crud
"""


async def create_db(db: Session, conf_db: schemas.ConfDBIn):
    db_info = models.ConfDB(**conf_db.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_db(db: Session, id_: int = None, name: str = None, ids: list = None):
    if id_:
        return db.query(models.ConfDB).filter(models.ConfDB.id == id_).all()

    if name:
        return db.query(models.ConfDB).filter(models.ConfDB.name == name).all()

    if ids:
        return db.query(models.ConfDB).filter(models.ConfDB.id.in_(ids)).all()

    return db.query(models.ConfDB).all()


async def update_db(db: Session, id_: int, conf_db: schemas.ConfDBIn):
    db.query(models.ConfDB).filter(
        models.ConfDB.id == id_
    ).update(conf_db.dict())
    db.commit()


async def del_db(db: Session, id_: int):
    db.query(models.ConfDB).filter(
        models.ConfDB.id == id_,
    ).delete()
    db.commit()


"""
统一响应列表的crud
"""


async def create_unify_res(db: Session, conf_unify_res: schemas.ConfUnifyResIn):
    db_info = models.ConfUnifyRes(**conf_unify_res.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_unify_res(db: Session, id_: int = None, name: str = None):
    if id_:
        return db.query(models.ConfUnifyRes).filter(models.ConfUnifyRes.id == id_).all()

    if name:
        return db.query(models.ConfUnifyRes).filter(models.ConfUnifyRes.name == name).all()

    return db.query(models.ConfUnifyRes).all()


async def update_unify_res(db: Session, id_: int, conf_unify_res: schemas.ConfUnifyResIn):
    db.query(models.ConfUnifyRes).filter(
        models.ConfUnifyRes.id == id_
    ).update(conf_unify_res.dict())
    db.commit()


async def del_unify_res(db: Session, id_: int):
    db.query(models.ConfUnifyRes).filter(
        models.ConfUnifyRes.id == id_,
    ).delete()
    db.commit()


"""
全局参数列表的crud
"""


async def create_customize(db: Session, conf_customize: schemas.ConfCustomizeIn):
    db_info = models.ConfCustomize(**conf_customize.dict())
    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    return db_info


async def get_customize(db: Session, id_: int = None, name: str = None, ids: list = None, key: str = None):
    if id_:
        return db.query(models.ConfCustomize).filter(models.ConfCustomize.id == id_).all()

    if name:
        return db.query(models.ConfCustomize).filter(models.ConfCustomize.name == name).all()

    if key:
        return db.query(models.ConfCustomize).filter(models.ConfCustomize.key == key).all()

    if ids:
        return db.query(models.ConfCustomize).filter(models.ConfCustomize.id.in_(ids)).all()

    return db.query(models.ConfCustomize).all()


async def update_customize(db: Session, id_: int, conf_customize: schemas.ConfCustomizeIn):
    db.query(models.ConfCustomize).filter(
        models.ConfCustomize.id == id_
    ).update(conf_customize.dict())
    db.commit()


async def del_customize(db: Session, id_: int):
    db.query(models.ConfCustomize).filter(
        models.ConfCustomize.id == id_,
    ).delete()
    db.commit()
