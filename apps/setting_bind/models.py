#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: models.py
@Time: 2023/7/27-16:05
"""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String
from apps.base_model import Base


class SettingSet(Base):
    """
    环境列表
    """
    __tablename__ = 'setting_set'

    name: Mapped[str] = mapped_column(String, index=True, comment='名称')
    host_ids: Mapped[list] = mapped_column(JSON, comment='域名id列表')
    customize_ids: Mapped[list] = mapped_column(JSON, comment='自定参数id列表')
    db_ids: Mapped[list] = mapped_column(JSON, comment='数据库id列表')
    api_case_ids: Mapped[list] = mapped_column(JSON, index=True, comment='api用例id列表')
    ui_case_ids: Mapped[list] = mapped_column(JSON, index=True, comment='api用例id列表')
