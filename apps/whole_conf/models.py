#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/4/16-14:42
"""

from sqlalchemy import Column, Integer, JSON, DateTime, String, func
from tools.database import Base


class ConfHost(Base):
    """
    域名列表
    """
    __tablename__ = 'conf_host'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    host = Column(String, comment='域名')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class ConfProject(Base):
    """
    项目列表（系统列表）
    """
    __tablename__ = 'conf_project'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    code = Column(String, comment='代号-编号')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class ConfDB(Base):
    """
    数据库配置
    """
    __tablename__ = 'conf_db'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    host = Column(String, comment='地址')
    user = Column(String, comment='用户')
    password = Column(String, comment='密码')
    database = Column(String, comment='数据库')
    port = Column(String, comment='端口')
    charset = Column(String, comment='编码')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class ConfUnifyRes(Base):
    """
    统一响应
    """
    __tablename__ = 'conf_unify_res'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    key = Column(String, comment='参数名')
    type = Column(String, comment='类型')
    value = Column(String, comment='参数值')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class ConfCustomize(Base):
    """
    自定义参数
    """
    __tablename__ = 'conf_customize'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, comment='名称')
    key = Column(String, comment='参数名')
    type = Column(String, comment='类型')
    value = Column(JSON, comment='参数值')

    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
