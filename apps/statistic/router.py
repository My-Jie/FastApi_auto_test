#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2023/7/12-14:43
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends
from .tool import api_free, ui_free
from depends import get_db

from apps import response_code
from apps.template import crud as temp_crud
from apps.case_service import crud as case_crud
from apps.case_ddt import crud as ddt_crud
from apps.case_ui import crud as ui_crud
from apps.api_report import crud as report_crud

statistic = APIRouter()


@statistic.get(
    '/api/charts/free',
    name='获取api用例的树状关系图',
)
async def e_charts_free(
        page: int = 1,
        size: int = 1000,
        db: AsyncSession = Depends(get_db)
):
    """
    由后端处理，输出统计数据，满足free的数据结构
    """
    temp_info = await temp_crud.get_temp_name(db=db, page=page, size=size)
    case_info = await case_crud.get_case_info(db=db, page=page, size=size)
    ddt_info = await ddt_crud.get_all(db=db)
    return await api_free(
        temp_info=temp_info,
        case_info=case_info,
        ddt_info=ddt_info
    )


@statistic.get(
    '/ui/charts/free',
    name='获取ui用例的树状关系图'
)
async def get_e_charts_free(
        page: int = 1,
        size: int = 1000,
        db: AsyncSession = Depends(get_db)
):
    temp_info = await ui_crud.get_playwright(db=db, page=page, size=size)
    case_info = await ui_crud.get_play_case_data(db=db)
    return await ui_free(
        temp_info=temp_info, case_info=case_info
    )


@statistic.get(
    '/get/playwright/echarts',
    name='获取UI数据统计',
    response_class=response_code.MyJSONResponse,
)
async def get_playwright_list(
        temp_name: str = None,
        page: int = 1,
        size: int = 1000,
        db: AsyncSession = Depends(get_db)
):
    """
    获取playwright列表
    """
    temp_info = await ui_crud.get_playwright(db=db, temp_name=temp_name, like=True, page=page, size=size)

    case_info = [
        {
            "name": f"{x.temp_name}",
            "case_id": x.id,
            "run_order": x.run_order,
            "success": x.success,
            "fail": x.fail,
        } for x in temp_info
    ]

    return case_info


@statistic.get(
    '/get/all/count',
    name='获取所有的统计数据计数'
)
async def get_all_statistic(db: AsyncSession = Depends(get_db)):
    return {
        'temp_count': await temp_crud.get_count(db=db),
        'case_count': await case_crud.get_count(db=db),
        'ddt_count': await ddt_crud.get_count(db=db),
        'ui_count': await ui_crud.get_count(db=db),
        'p_ddt_count': await ui_crud.get_ddt_count(db=db),
    }


@statistic.get(
    '/get/case/count',
    name='获取用例统计数据'
)
async def get_case_count(db: AsyncSession = Depends(get_db)):
    return {
        'case_count': await case_crud.get_count(db=db),
        'case_today': await case_crud.get_count(db=db, today=True),
        'api_count': await case_crud.get_api_count(db=db),
        'api_today': await case_crud.get_api_count(db=db, today=True),
        'run_count': await report_crud.get_report_count(db),
        'run_today': await report_crud.get_report_count(db, today=True),
        'ddt_count': await ddt_crud.get_count(db=db),
        'ddt_today': await ddt_crud.get_count(db=db, today=True),
    }


@statistic.get(
    '/get/temp/count',
    name='获取模板统计数据'
)
async def get_temp_count(db: AsyncSession = Depends(get_db)):
    return {
        'temp_count': await temp_crud.get_count(db=db),
        'temp_today': await temp_crud.get_count(db=db, today=True),
        'api_count': await temp_crud.get_api_count(db=db),
        'api_today': await temp_crud.get_api_count(db=db, today=True),
        'case_count': await case_crud.get_count(db=db),
        'case_today': await case_crud.get_count(db=db, today=True),
    }
