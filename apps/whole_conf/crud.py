#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: crud.py
@Time: 2023/4/16-14:42
"""

from sqlalchemy import func, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from apps.whole_conf import models, schemas

"""
域名列表的crud
"""


async def create_host(db: AsyncSession, conf_host: schemas.ConfHostIn):
    db_info = models.ConfHost(**conf_host.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_host(db: AsyncSession, id_: int = None, name: str = None, ids: list = None):
    if id_:
        result = await db.execute(
            select(models.ConfHost).filter(models.ConfHost.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.ConfHost).filter(models.ConfHost.name == name)
        )
        return result.scalars().all()

    if ids:
        result = await db.execute(
            select(models.ConfHost).filter(models.ConfHost.id.in_(ids))
        )
        return result.scalars().all()

    result = await db.execute(select(models.ConfHost))
    return result.scalars().all()


async def update_host(db: AsyncSession, id_: int, conf_host: schemas.ConfHostIn):
    """

    :param db:
    :param id_:
    :param conf_host:
    :return:
    """
    await db.execute(
        update(models.ConfHost).where(models.ConfHost.id == id_).values(conf_host.dict())
    )
    await db.commit()


async def del_host(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.ConfHost).where(models.ConfHost.id == id_)
    )
    await db.commit()


"""
项目列表的crud
"""


async def create_project(db: AsyncSession, conf_project: schemas.ConfProjectIn):
    db_info = models.ConfProject(**conf_project.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_project(db: AsyncSession, id_: int = None, name: str = None):
    if id_:
        result = await db.execute(
            select(models.ConfProject).filter(models.ConfProject.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.ConfProject).filter(models.ConfProject.name == name)
        )
        return result.scalars().all()

    result = await db.execute(select(models.ConfProject))
    return result.scalars().all()


async def get_project_code(db: AsyncSession, id_: int = None):
    result = await db.execute(
        select(models.ConfProject.code).filter(models.ConfProject.id == id_)
    )
    db_info = result.scalars().all()
    if db_info:
        return db_info[0]


async def update_project(db: AsyncSession, id_: int, conf_project: schemas.ConfProjectIn):
    await db.execute(
        update(models.ConfProject).where(models.ConfProject.id == id_).values(conf_project.dict())
    )
    await db.commit()


async def del_project(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.ConfProject).where(models.ConfProject.id == id_)
    )
    await db.commit()


"""
数据库列表的crud
"""


async def create_db(db: AsyncSession, conf_db: schemas.ConfDBIn):
    db_info = models.ConfDB(**conf_db.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_db(db: AsyncSession, id_: int = None, name: str = None, ids: list = None):
    if id_:
        result = await db.execute(
            select(models.ConfDB).filter(models.ConfDB.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.ConfDB).filter(models.ConfDB.name == name)
        )
        return result.scalars().all()

    if ids:
        result = await db.execute(
            select(models.ConfDB).filter(models.ConfDB.id.in_(ids))
        )
        return result.scalars().all()

    result = await db.execute(select(models.ConfDB))
    return result.scalars().all()


async def update_db(db: AsyncSession, id_: int, conf_db: schemas.ConfDBIn):
    await db.execute(
        update(models.ConfDB).where(models.ConfDB.id == id_).values(conf_db.dict())
    )
    await db.commit()


async def del_db(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.ConfDB).where(models.ConfDB.id == id_)
    )
    await db.commit()


"""
统一响应列表的crud
"""


async def create_unify_res(db: AsyncSession, conf_unify_res: schemas.ConfUnifyResIn):
    db_info = models.ConfUnifyRes(**conf_unify_res.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_unify_res(db: AsyncSession, id_: int = None, name: str = None):
    if id_:
        result = await db.execute(
            select(models.ConfUnifyRes).filter(models.ConfUnifyRes.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.ConfUnifyRes).filter(models.ConfUnifyRes.name == name)
        )
        return result.scalars().all()

    result = await db.execute(select(models.ConfUnifyRes))
    return result.scalars().all()


async def update_unify_res(db: AsyncSession, id_: int, conf_unify_res: schemas.ConfUnifyResIn):
    await db.execute(
        update(models.ConfUnifyRes).where(models.ConfUnifyRes.id == id_).values(conf_unify_res.dict())
    )
    await db.commit()


async def del_unify_res(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.ConfUnifyRes).where(models.ConfUnifyRes.id == id_)
    )
    await db.commit()


"""
全局参数列表的crud
"""


async def create_customize(db: AsyncSession, conf_customize: schemas.ConfCustomizeIn):
    db_info = models.ConfCustomize(**conf_customize.dict())
    db.add(db_info)
    await db.commit()
    await db.refresh(db_info)
    return db_info


async def get_customize(db: AsyncSession, id_: int = None, name: str = None, ids: list = None, key: str = None):
    if id_:
        result = await db.execute(
            select(models.ConfCustomize).filter(models.ConfCustomize.id == id_)
        )
        return result.scalars().all()

    if name:
        result = await db.execute(
            select(models.ConfCustomize).filter(models.ConfCustomize.name == name)
        )
        return result.scalars().all()

    if key:
        result = await db.execute(
            select(models.ConfCustomize).filter(models.ConfCustomize.key == key)
        )
        return result.scalars().all()

    if ids:
        result = await db.execute(
            select(models.ConfCustomize).filter(models.ConfCustomize.id.in_(ids))
        )
        return result.scalars().all()

    result = await db.execute(select(models.ConfCustomize))
    return result.scalars().all()


async def update_customize(db: AsyncSession, id_: int, conf_customize: schemas.ConfCustomizeIn):
    await db.execute(
        update(models.ConfCustomize).where(models.ConfCustomize.id == id_).values(conf_customize.dict())
    )
    await db.commit()


async def del_customize(db: AsyncSession, id_: int):
    await db.execute(
        delete(models.ConfCustomize).where(models.ConfCustomize.id == id_)
    )
    await db.commit()
