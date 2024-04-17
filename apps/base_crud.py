#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：base_crud.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/3/28 16:47 
"""

import abc
from typing import List, Type, Callable
from pydantic import BaseModel
from apps.base_model import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class _BaseCRUD(abc.ABC):
    """
    基础的CRUD，提供简单的操作，只能被继承，不能被实例化
    """

    def __init__(self, model: Type[Base], async_session: AsyncSession):
        self.model = model
        self.async_session = async_session

    async def create(self, objs: List[BaseModel]) -> List[Base]:
        db_objs = [self.model(**obj.dict()) for obj in objs]
        self.async_session.add_all(db_objs)
        await self.async_session.commit()
        await self.async_session.refresh(db_objs)
        return db_objs

    async def query(self, obj_id: int, size: int, page: int):
        """
        按表的自增id查询数据，返回列表
        :param obj_id:
        :param size:
        :param page:
        :return:
        """
        result = await self.async_session.execute(
            select(self.model).where(self.model.id == obj_id).order_by(
                self.model.id
            ).offset(size * (page - 1)).limit(size)
        )
        return result.scalars().all()


class ComplexCRUD(_BaseCRUD):
    """
    apps中的CRUD，继承这个类，可以提供复杂的操作
    """
    pass
