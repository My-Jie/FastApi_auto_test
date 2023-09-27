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
from apps.api_pool.router import pool
from apps.run_case.router import run_case
from apps.own_params_rep.router import own_rep
from apps.whole_conf.router import conf
from apps.setting_bind.router import setting_
from apps.statistic.router import statistic
from apps.status.router import ws_app
from tools.load_allure import load_allure_reports
from fastapi.staticfiles import StaticFiles
from apps import response_code

from tools.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    include_in_=True,
    title='随便测测'
)


@app.get('/helpInfo', name='操作概要说明', tags=['Help'])
async def help_info():
    return await response_code.resp_200(data={
        'order': {
            '/template/upload/har': '上传Charles的Har文件-先解析-再写入',
            '/caseService/init/data/json': '下载预处理后的模板数据-Json',
            '/template/data/list': '查询模板接口原始数据',
            '/caseService/upload/json': '上传测试数据-Json',
            '/runCase/': '按用例执行',
        },
        'description': '将模板数据Json下载下来后，通常需要对照原始数据进行jsonPath表达式进行编辑，编辑完成即可上传Json',
        'tips': TIPS
    })


app.include_router(template, prefix='/template', tags=['[模板]测试场景'])
app.include_router(case_service, prefix='/caseService', tags=['[用例]业务接口'])
app.include_router(case_ddt, prefix='/caseDdt', tags=['[用例]数据驱动'])
app.include_router(case_ui, prefix='/caseUi', tags=['[用例]UI测试'])
app.include_router(run_case, prefix='/runCase', tags=['执行测试'])
app.include_router(own_rep, prefix='/ownRep', tags=['参数替换'])
app.include_router(statistic, prefix='/statistic', tags=['数据统计'])
app.include_router(conf, prefix='/conf', tags=['全局配置'])
app.include_router(setting_, prefix='/setting', tags=['环境组装'])
app.include_router(pool, prefix='/YApi', tags=['YApi接口池'])
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
