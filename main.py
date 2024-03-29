#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/3-16:40
"""

import uvicorn
from fastapi import FastAPI
from tools.tips import TIPS
from tools.read_setting import setting
from apps.template.router import template
from apps.case_service.router import case_service
from apps.case_ddt.router import case_ddt
from apps.case_ui.router import case_ui
from apps.run_case.router import run_case
from apps.whole_conf.router import conf
from apps.setting_bind.router import setting_
from apps.statistic.router import statistic
from apps.api_report.router import api_report
from apps.status.router import ws_app
from tools.load_allure import load_allure_reports
from fastapi.staticfiles import StaticFiles
from apps import response_code

from tools.database import async_engine
from apps.base_model import Base

app = FastAPI(
    include_in_=True,
    title='anyTest'
)


@app.on_event('startup')
async def start_up():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event('shutdown')
async def shutdown():
    await async_engine.dispose()


app.include_router(template, prefix='/template', tags=['[模板]测试场景'])
app.include_router(case_service, prefix='/caseService', tags=['[用例]业务接口'])
app.include_router(case_ddt, prefix='/caseDdt', tags=['[用例]数据驱动'])
app.include_router(case_ui, prefix='/caseUi', tags=['[用例]UI测试'])
app.include_router(run_case, prefix='/runCase', tags=['执行测试'])
app.include_router(statistic, prefix='/statistic', tags=['数据统计'])
app.include_router(conf, prefix='/conf', tags=['全局配置'])
app.include_router(setting_, prefix='/setting', tags=['环境组装'])
app.include_router(api_report, prefix='/report', tags=['接口报告'])
app.include_router(ws_app, prefix='/ws', tags=['状态'])


# 测试报告路径
@app.get('/allure', name='allure测试报告地址', tags=['测试报告'])
async def allure():
    return await response_code.resp_200(data={'allure_report': f"{setting['host']}" + "{case_id}/{run_order}"})


app.mount('/index.html', StaticFiles(directory='static', html=True))

load_allure_reports(app=app, allure_dir=setting['allure_path'])
load_allure_reports(app=app, allure_dir=setting['allure_path_ui'], ui=True)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False)
