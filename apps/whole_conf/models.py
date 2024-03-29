#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/4/16-14:42
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String
from apps.base_model import Base


class ConfBase(Base):
    __abstract__ = True

    name: Mapped[str] = mapped_column(String, index=True, comment='名称')


class ConfHost(ConfBase):
    """
    域名列表
    """
    __tablename__ = 'conf_host'

    host: Mapped[str] = mapped_column(String, comment='域名')


class ConfProject(ConfBase):
    """
    项目列表（系统列表）
    """
    __tablename__ = 'conf_project'

    code: Mapped[str] = mapped_column(String, comment='代号-编号')


class ConfDB(ConfBase):
    """
    数据库配置
    """
    __tablename__ = 'conf_db'

    host: Mapped[str] = mapped_column(String, comment='地址')
    user: Mapped[str] = mapped_column(String, comment='用户')
    password: Mapped[str] = mapped_column(String, comment='密码')
    database: Mapped[str] = mapped_column(String, comment='数据库')
    port: Mapped[str] = mapped_column(String, comment='端口')
    charset: Mapped[str] = mapped_column(String, comment='编码')


class ConfJsonObj(ConfBase):
    __abstract__ = True

    key: Mapped[str] = mapped_column(String, comment='参数名')
    type: Mapped[str] = mapped_column(String, comment='类型')
    value: Mapped[str] = mapped_column(JSON, comment='参数值')


class ConfUnifyRes(ConfJsonObj):
    """
    统一响应
    """
    __tablename__ = 'conf_unify_res'


class ConfCustomize(ConfJsonObj):
    """
    自定义参数
    """
    __tablename__ = 'conf_customize'
