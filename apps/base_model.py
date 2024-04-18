#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：base_model.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/3/27 17:22 
"""

from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, DateTime


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        sort_order=-1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment='创建时间'
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment='更新时间'
    )
