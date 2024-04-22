#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: router.py
@Time: 2022/8/20-22:00
"""

import os
import json
import time
from typing import List, Any
from fastapi import APIRouter, UploadFile, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import FileResponse
from starlette.background import BackgroundTask
from depends import get_db
from apps import response_code
from tools.check_case_json import CheckJson
from tools import OperationJson, ExtractParamsPath, RepData, filter_number
from .tool import GetCaseDataInfo, check, jsonpath_count, aim

from apps.template import crud as temp_crud
from apps.case_service import crud, schemas
from apps.case_ddt import crud as ddt_crud
from apps.case_service.tool import insert, cover_insert
from apps.template.tool import GenerateCase
from apps.run_case import CASE_RESPONSE

case_service = APIRouter()


@case_service.get(
    '/download/init/data/json',
    response_model=schemas.TestCaseDataOut,
    response_model_exclude_unset=True,
    name='下载预处理后的模板数据-json',
)
async def download_case_data(
        temp_id: int,
        mode: schemas.ModeEnum,
        fail_stop: bool,
        db: AsyncSession = Depends(get_db)
):
    """
    自动处理部分接口上下级关联数据\n
    json格式化数据下载
    """
    if mode != schemas.ModeEnum.service:
        return await response_code.resp_400(message=f'该模式仅支持{schemas.ModeEnum.service}模式')

    template_data = await temp_crud.get_template_data(db=db, temp_id=temp_id)
    if template_data:
        temp_name = await temp_crud.get_temp_name(db=db, temp_id=temp_id)
        test_data = await GenerateCase().read_template_to_api(
            db=db,
            temp_name=temp_name[0].temp_name,
            mode=mode,
            fail_stop=fail_stop,
            template_data=template_data
        )
        path = f'./files/json/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.json'
        await OperationJson.write(path=path, data=test_data)
        return FileResponse(
            path=path,
            filename=f'{temp_name[0].temp_name}.json',
            background=BackgroundTask(lambda: os.remove(path))
        )

    return await response_code.resp_400()


@case_service.post(
    '/upload/json',
    response_model=schemas.TestCaseOut,
    response_class=response_code.MyJSONResponse,
    name='上传测试数据-json'
)
async def test_case_upload_json(
        temp_id: int,
        file: UploadFile,
        case_id: int = None,
        case_name: str = None,
        cover: bool = False,
        db: AsyncSession = Depends(get_db)
):
    """
    上传json文件，解析后储存测试数据
    """

    if file.content_type != 'application/json':
        return await response_code.resp_400(message='文件类型错误，只支持json格式文件')

    db_temp = await temp_crud.get_temp_name(db=db, temp_id=temp_id)
    if not db_temp:
        return await response_code.resp_400(message='模板不存在')

    # 校验数据
    try:
        case_data = json.loads(file.file.read().decode('utf-8'))
    except json.decoder.JSONDecodeError as e:
        return await response_code.resp_400(message=f'json文件格式有错误: {str(e)}')

    try:
        msg_list = await CheckJson.check_to_service(db=db, temp_id=temp_id, case_data=case_data['data'])
    except (TypeError, KeyError):
        return await response_code.resp_400(message='文件格式或内容有误')
    if msg_list:
        return await response_code.resp_400(data=msg_list)

    if cover:  # 覆盖
        if not case_id:
            return await response_code.resp_400(message='未输入case_id')

        if not await crud.get_case_info(db=db, case_id=case_id):
            return await response_code.resp_400(message='未查询到用例数据')

        return await cover_insert(db=db, case_id=case_id, case_data=case_data)
    else:  # 不覆盖
        if not case_name:
            return await response_code.resp_400(message='未输入case_name')
        return await insert(db=db, case_name=case_name, temp_id=db_temp[0].id, case_data=case_data)


@case_service.get(
    '/temp/to/case',
    name='模板转为用例'
)
async def temp_to_case(
        temp_id: int,
        case_name: str,
        case_id: int = None,
        cover: bool = False,
        fail_stop: bool = True,
        db: AsyncSession = Depends(get_db)
):
    db_temp = await temp_crud.get_temp_name(db=db, temp_id=temp_id)
    if not db_temp:
        return await response_code.resp_400(message='模板不存在')

    template_data = await temp_crud.get_template_data(db=db, temp_id=temp_id)
    test_data = await GenerateCase().read_template_to_api(
        db=db,
        temp_name=db_temp[0].temp_name,
        mode='service',
        fail_stop=fail_stop,
        template_data=template_data
    )

    if not cover:  # 覆盖
        if not case_id:
            return await response_code.resp_400(message='未输入case_id')

        case_info = await crud.get_case_info(db=db, case_id=case_id)
        if not case_info:
            return await response_code.resp_400(message='没有这个case_id')
        if case_info[0].temp_id != temp_id:
            return await response_code.resp_400(message='这个case_id没有绑定到这个模板')

        await cover_insert(db=db, case_id=case_id, case_data=test_data)
        return await response_code.resp_200(message='覆盖成功', data={'case_id': case_id})
    else:  # 新增
        if not case_name:
            return await response_code.resp_400(message='未输入case_name')
        new_case_info = await insert(db=db, case_name=case_name, temp_id=db_temp[0].id, case_data=test_data)
        return await response_code.resp_200(message='新增成功', data={'case_id': new_case_info.id})


@case_service.get(
    '/data/{case_id}',
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='查看用例测试数据'
)
async def case_data_info(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    查看测试数据
    """
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return case_info

    temp_info = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)

    return await GetCaseDataInfo().service(
        temp_info=temp_info,
        case_info=case_info,
        case_data_info=await crud.get_case_data(db=db, case_id=case_id)
    )


@case_service.get(
    '/download/data/{case_id}',
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='下载测试数据-Json'
)
async def download_case_data_info(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    下载测试数据
    """
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return await response_code.resp_400()

    temp_info = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)

    case_data = await GetCaseDataInfo().service(
        temp_info=temp_info,
        case_info=case_info,
        case_data_info=await crud.get_case_data(db=db, case_id=case_id)
    )

    path = f'./files/json/{time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))}.json'
    await OperationJson.write(path=path, data=case_data)
    return FileResponse(
        path=path,
        filename=f'{case_info[0].case_name}.json',
        background=BackgroundTask(lambda: os.remove(path))
    )


@case_service.get(
    '/data/case/list',
    response_model=schemas.PaginationTestCaseInfo,
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='查看测试用例列表'
)
async def case_data_list(
        case_name: str = '',
        page: int = 1,
        size: int = 10,
        outline: bool = True,
        db: AsyncSession = Depends(get_db)
):
    """
    查看测试用例列表
    """
    test_case = await crud.get_case_all_info(db=db, case_name=case_name, page=page, size=size)

    case_info = []
    for case in test_case:
        case_info.append(
            {
                "name": f"{case[2]}-{case[1]}-{case[0].case_name}",
                "case_name": f"{case[0].case_name}",
                "temp_name": f"{case[2]}-{case[1]}",
                "case_id": case[0].id,
                "api_count": case[0].case_count,
                "run_order": case[0].run_order,
                "success": case[0].success,
                "fail": case[0].fail,
                "mode": case[0].mode,
                "report": case[3] if case[3] else '1970-01-01 00:00:00',
                "created_at": case[0].created_at,
                "updated_at": case[0].updated_at
            } if outline is False else {
                "name": f"{case[2]}-{case[1]}-{case[0].case_name}",
                "case_name": f"{case[0].case_name}",
                "temp_name": f"{case[2]}-{case[1]}",
                "case_id": case[0].id
            }
        )
    return {
        'items': case_info,
        'total': await crud.get_count(db=db, case_name=case_name),
        'page': page,
        'size': size
    }


@case_service.delete(
    '/del/{case_id}',
    name='删除测试数据'
)
async def del_case(case_id: int, db: AsyncSession = Depends(get_db)):
    if not await crud.get_case_info(db=db, case_id=case_id):
        return await response_code.resp_400()
    await crud.del_case_data(db=db, case_id=case_id)
    await ddt_crud.del_test_gather(db=db, case_id=case_id)

    return await response_code.resp_200(message=f'用例{case_id}删除成功')


@case_service.get(
    '/query/urls',
    response_model=List[schemas.TestCaseDataOut2],
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='查询url数据'
)
async def query_urls(url: str = Query(..., min_length=5), db: AsyncSession = Depends(get_db)):
    return await crud.get_urls(db=db, url=url)


@case_service.put(
    '/update/urls',
    response_model=List[schemas.TestCaseDataOut2],
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='批量修改url'
)
async def update_urls(
        old_url: str = Query(..., min_length=5),
        new_url: str = Query(..., min_length=5),
        db: AsyncSession = Depends(get_db)
):
    return await crud.update_urls(db=db, old_url=old_url, new_url=new_url)


@case_service.put(
    '/name/edit',
    name='修改用例名称'
)
async def name_edit(un: schemas.UpdateName, db: AsyncSession = Depends(get_db)):
    """
    修改用例名称
    """
    return await crud.put_case_name(
        db=db,
        case_id=un.case_id,
        new_name=un.new_name
    )


@case_service.get(
    '/query/api/info',
    response_model=schemas.TestCaseDataOut1,
    response_class=response_code.MyJSONResponse,
    response_model_exclude_unset=True,
    name='按用例/序号查看API数据'
)
async def get_api_info(case_id: int, number: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_api_info(db=db, case_id=case_id, number=number)


@case_service.put(
    '/update/api/info',
    name='按用例/序号修改API数据'
)
async def put_api_info(api_info: schemas.TestCaseDataOut1, db: AsyncSession = Depends(get_db)):
    if await crud.update_api_info(db=db, api_info=api_info):
        return await response_code.resp_200()
    else:
        return await response_code.resp_400(message='修改失败，未获取到内容')


@case_service.put(
    '/swap/one',
    name='编排用例数据的顺序-单次'
)
async def swap_one(one: schemas.SwapOne, db: AsyncSession = Depends(get_db)):
    """
    单次替换用例中API的顺序-索引号
    """
    case_data = await crud.get_case_data(db=db, case_id=one.case_id)
    if not case_data:
        return case_data

    # 判断序号
    numbers = {x.number: x.id for x in case_data}
    null_num = [num for num in [one.old_number, one.new_number] if num not in [x for x in numbers]]
    if null_num:
        return await response_code.resp_400(message=f'序号{null_num} 不在该用例的序号中')

    # 替换number序号
    id_ = numbers[one.old_number]
    await crud.update_api_number(db=db, case_id=one.case_id, id_=id_, new_number=one.new_number)
    id_ = numbers[one.new_number]
    await crud.update_api_number(db=db, case_id=one.case_id, id_=id_, new_number=one.old_number)

    return await response_code.resp_200(
        data={
            'old_number': one.old_number,
            'new_number': one.new_number
        }
    )


@case_service.put(
    '/swap/many',
    name='编排用例数据的顺序-全部'
)
async def swap_many(many: schemas.SwapMany, db: AsyncSession = Depends(get_db)):
    """
    依次替换用例中API的顺序-索引号
    """
    case_data = await crud.get_case_data(db=db, case_id=many.case_id)
    if not case_data:
        return case_data

    if len(set(many.new_numbers)) != len(case_data):
        return await response_code.resp_400(
            message=f'new_numbers长度：{len(set(many.new_numbers))}，'
                    f'与数据库中的numbers长度：{len(case_data)}，不一致'
        )

    # 判断序号
    numbers = {x.number: x.id for x in case_data}
    null_num = [num for num in many.new_numbers if num not in [x for x in numbers]]
    if null_num:
        return await response_code.resp_400(message=f'序号{null_num} 不在该模板的序号中')

    # 替换number序号
    num_info = False
    for x in range(len(many.new_numbers)):
        if x != many.new_numbers[x]:
            await crud.update_api_number(db=db, case_id=many.case_id, id_=numbers[x], new_number=many.new_numbers[x])
            num_info = True

    return await response_code.resp_200(
        data={
            'old_number': [x for x in numbers],
            'new_number': many.new_numbers
        },
        message='Success 请注意-需要同步修改用例文件中 JsonPath 表达式的序号引用'
    ) if num_info else await response_code.resp_200(
        message='数据无变化'
    )


@case_service.put(
    '/set/api/config',
    name='设置用例配置'
)
async def set_api_config(sac: schemas.SetApiConfig, db: AsyncSession = Depends(get_db)):
    """
    设置每个接口的配置信息
    """
    if not sac.config:
        return await response_code.resp_400(message='无效配置内容')

    case_data = await crud.get_case_data(db=db, case_id=sac.case_id, number=sac.number)
    if not case_data:
        return await response_code.resp_400(message='没有获取到这个用例配置')

    # new_config = {k: v for k, v in sac.config if v is not None and v != []}

    await crud.set_case_info(db=db, case_id=sac.case_id, number=sac.number, config=sac.config)

    return await response_code.resp_200()


@case_service.put(
    '/set/api/description',
    name='设置描述信息'
)
async def set_api_description(sad: schemas.SetApiDescription, db: AsyncSession = Depends(get_db)):
    """
    设置每个接口的描述信息
    """
    # if not sad.description:
    #     return await response_code.resp_400(message='无效描述内容')

    case_data = await crud.get_case_data(db=db, case_id=sad.case_id, number=sad.number)
    if not case_data:
        return await response_code.resp_400(message='没有获取到这个用例描述')

    await crud.set_case_description(db=db, case_id=sad.case_id, number=sad.number, description=sad.description)

    return await response_code.resp_200()


@case_service.put(
    '/set/api/check',
    name='设置校验内容'
)
async def set_api_check(sac: schemas.SetApiCheck, db: AsyncSession = Depends(get_db)):
    """
    设置每个接口的校验信息
    """
    case_data = await crud.get_case_data(db=db, case_id=sac.case_id, number=sac.number)
    if not case_data:
        return await response_code.resp_400(message='没有获取到这个用例配置')

    if not sac.check.key:
        return await response_code.resp_400(message='无效的key')

    check_info = case_data[0].check

    key_ = sac.check.key.strip()
    if sac.type == 'edit':
        if check(check=sac.check) != True:
            return await response_code.resp_400(message='数据逻辑校验未通过')
        if sac.check.type == 'boolean':
            if sac.check.value == 1:
                check_info[key_] = [sac.check.s, True] if sac.check.s != '==' else True
            else:
                check_info[key_] = [sac.check.s, False] if sac.check.s != '==' else False
        elif sac.check.type == 'number':
            check_info[key_] = [sac.check.s, sac.check.value] if sac.check.s != '==' else sac.check.value
        elif sac.check.type == 'string':
            check_info[key_] = [sac.check.s, str(sac.check.value)] if sac.check.s != '==' else str(sac.check.value)
        elif sac.check.type == 'null':
            check_info[key_] = [sac.check.s, None] if sac.check.s != '==' else None
        else:
            check_info[key_] = [sac.check.s, sac.check.value] if sac.check.s != '==' else sac.check.value

    if sac.type == 'del':
        if check_info.get(key_, '_') != '_':
            del check_info[key_]

    await crud.set_case_info(db=db, case_id=sac.case_id, number=sac.number, check=check_info)
    return await response_code.resp_200()


@case_service.put(
    '/set/api/params/data',
    name='更新用例params/data数据'
)
async def set_params_data(spd: schemas.SedParamsData, db: AsyncSession = Depends(get_db)):
    """
    更新用例的params数据或data数据
    """
    if not await crud.get_case_data(db=db, case_id=spd.case_id, number=spd.number):
        return await response_code.resp_400(message='没有获取到这个用例数据')

    if spd.type.lower() == 'params':
        await crud.set_case_info(db=db, case_id=spd.case_id, number=spd.number, params=spd.data_info)
    elif spd.type.lower() == 'data':
        await crud.set_case_info(db=db, case_id=spd.case_id, number=spd.number, data=spd.data_info)
    elif spd.type.lower() == 'headers':
        await crud.set_case_info(db=db, case_id=spd.case_id, number=spd.number, headers=spd.data_info)
    else:
        return await response_code.resp_400()
    return await response_code.resp_200()


@case_service.put(
    '/set/api/header',
    name='设置请求头内容'
)
async def set_api_check(sac: schemas.setApiHeader, db: AsyncSession = Depends(get_db)):
    """
    设置每个接口的校验信息
    """
    case_data = await crud.get_case_data(db=db, case_id=sac.case_id, number=sac.number)
    if not case_data:
        return await response_code.resp_400(message='没有获取到这个用例请求头')

    headers_info = case_data[0].headers
    key_ = sac.header.key.strip()
    if sac.type == 'edit':
        headers_info[key_] = sac.header.value

    if sac.type == 'del':
        if headers_info.get(key_, '_') != '_':
            del headers_info[key_]

    await crud.set_case_info(db=db, case_id=sac.case_id, number=sac.number, headers=headers_info)
    return await response_code.resp_200()


@case_service.get(
    '/response/jsonpath/list',
    name='从原始数据response/response_headers中获取jsonpath表达式',
)
async def get_response_json_path(
        case_id: int,
        extract_contents: Any,
        data_type: schemas.RepType,
        key_value: schemas.KeyValueType,
        ext_type: schemas.ExtType,
        db: AsyncSession = Depends(get_db)
):
    """
    通过用例id从原始数据中获取jsonpath表达式
    """
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return await case_info

    temp_data = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)
    value_list = ExtractParamsPath.get_value_path(
        extract_contents=extract_contents,
        my_data=temp_data,
        type_=data_type,
        key_value=key_value,
        ext_type=ext_type
    )
    return await response_code.resp_200(
        data=value_list
    )


@case_service.get(
    '/casedata/jsonpath/list',
    name='从测试数据中获取会被替换的数据'
)
async def get_case_data_json_path(
        case_id: int,
        extract_contents: Any,
        new_str: str,
        key_value: schemas.KeyValueType,
        ext_type: schemas.ExtType,
        db: AsyncSession = Depends(get_db)):
    """
    通过用例id从测试数据url、params、data中预览会被替换的数据
    """

    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return await response_code.resp_400(message='没有获取到这个用例id')

    case_data = await crud.get_case_data(db=db, case_id=case_id)

    # 预览查询================================#
    url_list = ExtractParamsPath.get_url_path(
        extract_contents=extract_contents,
        my_data=case_data,
    )
    params_list = ExtractParamsPath.get_value_path(
        extract_contents=extract_contents,
        my_data=case_data,
        type_=schemas.RepType.params,
        key_value=key_value,
        ext_type=ext_type
    )
    data_list = ExtractParamsPath.get_value_path(
        extract_contents=extract_contents,
        my_data=case_data,
        type_=schemas.RepType.data,
        key_value=key_value,
        ext_type=ext_type
    )
    headers_list = ExtractParamsPath.get_value_path(
        extract_contents=extract_contents,
        my_data=case_data,
        type_=schemas.RepType.headers,
        key_value=key_value,
        ext_type=ext_type
    )

    # 对比数据================================#
    RepData.rep_url(url_list=url_list, new_str=new_str, extract_contents=extract_contents)
    RepData.rep_json(json_data=params_list, case_data=case_data, new_str=new_str, type_='params')
    RepData.rep_json(json_data=data_list, case_data=case_data, new_str=new_str, type_='data')
    RepData.rep_json(json_data=headers_list, case_data=case_data, new_str=new_str, type_='headers')

    # 过滤下number小于等于查询number的数据
    await filter_number(url_list)
    await filter_number(params_list)
    await filter_number(data_list)

    if not any(
            (
                    url_list['extract_contents'],
                    params_list['extract_contents'],
                    data_list['extract_contents'],
                    headers_list['extract_contents'],
            )
    ):
        return await response_code.resp_400()

    return await response_code.resp_200(
        data={
            'url_list': url_list,
            'params_list': params_list,
            'data_list': data_list,
            'headers_list': headers_list
        }
    )


@case_service.post(
    '/replace/one/casedata',
    name='替换单个测试数据'
)
async def replace_one_casedata(
        case_id: int,
        number: int,
        old_data: str,
        new_data: str,
        rep: bool,
        data_type: str,
        db: AsyncSession = Depends(get_db)
):
    """
    单个用例替换单条api数据
    """
    if not old_data or not new_data:
        return await response_code.resp_400(message='字符串不能为空')

    if data_type not in ['url', 'data', 'params', 'headers']:
        return await response_code.resp_400(message='不支持这个data_type')

    case_info = await crud.get_case_data(db=db, case_id=case_id)
    if not case_info:
        return await response_code.resp_400(message='没有获取到这个用例id')

    if number not in [x.number for x in case_info]:
        return await response_code.resp_400(message='这个用例没有这个number')

    if rep:
        await crud.set_case_data(
            db=db,
            case_id=case_id,
            number=number,
            old_data=old_data,
            new_data=new_data,
            type_=data_type
        )
    else:
        await crud.set_case_data(
            db=db,
            case_id=case_id,
            number=number,
            old_data=new_data,
            new_data=old_data,
            type_=data_type
        )

    return await response_code.resp_200()


@case_service.get(
    '/copy/case',
    name='复制测试用例数据，形成新的测试用例'
)
async def copy_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    复制测试用例，形成新的测试用例
    """
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return await response_code.resp_400(message='没有获取到这个用例id')

    case_name = case_info[0].case_name + ' - 副本'
    case_data = await crud.get_case_data(db=db, case_id=case_id)
    case_data = [{
        'number': x.number,
        'path': x.path,
        'headers': x.headers,
        'params': x.params,
        'data': x.data,
        'file': x.file,
        'check': x.check,
        'description': x.description,
        'config': x.config,
    } for x in case_data]

    case_data = {
        'mode': 'service',
        'data': case_data
    }
    return await insert(db=db, case_name=case_name, temp_id=case_info[0].temp_id, case_data=dict(**case_data))


@case_service.get(
    '/get/apiInfo',
    name='按用例id和number获取历史模板的path, params, data, herders, response'
)
async def get_response(case_id: int, number: int, type_: str, db: AsyncSession = Depends(get_db)):
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return case_info

    temp_info = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id, numbers=[number])

    return_dict = {
        'path': temp_info[0].path,
        'params': temp_info[0].params,
        'data': temp_info[0].data,
        'headers': temp_info[0].headers,
        'response': temp_info[0].response,
    }

    return return_dict.get(type_)


@case_service.get(
    '/get/jsonpath',
    name='获取用例中jsonpath的引用关系'
)
async def get_jsonpath(case_id: int, jsonpath_name: str = None, db: AsyncSession = Depends(get_db)):
    case_info = await crud.get_case_info(db=db, case_id=case_id)
    if not case_info:
        return case_info

    case_list = await crud.get_case_data(db=db, case_id=case_info[0].id)
    temp_list = await temp_crud.get_template_data(db=db, temp_id=case_info[0].temp_id)

    data_count = jsonpath_count(
        case_list=case_list,
        temp_list=temp_list,
        run_case=CASE_RESPONSE.get(case_id, []),
        get_temp_value=True
    )

    # 查询单个jsonpath的追踪详情
    if jsonpath_name is not None:
        for json_str in data_count:
            if json_str['jsonpath'] == jsonpath_name:
                start_number = json_str['jsonpath'].split('.')[0].replace('{{', '')
                return {
                    'source': 'headers' if '$h' in json_str['jsonpath'] else 'response',
                    'start_number': start_number,
                    'query_info': json_str,
                    'jsonpath_list': await aim(db=db, case_id=case_id, json_str=json_str)
                }
        else:
            return await response_code.resp_400(message='没有找到这个jsonpath')

    return data_count


@case_service.get(
    '/detail/api/{detail_id}',
    name='模板api详情',
    response_model=schemas.TestCaseDataOut2,
    response_model_exclude_unset=True,
)
async def detail_api(detail_id: int, db: AsyncSession = Depends(get_db)):
    """
    查询用例api详情
    """
    case_detail = await crud.get_case_detail(db=db, detail_id=detail_id)
    if not case_detail:
        return await response_code.resp_400(message='没有获取到这个用例api详情数据')
    return case_detail


@case_service.put(
    '/detail/api/path',
    name='修改api路径'
)
async def update_api_path(
        detail_id: int,
        new_path: str,
        db: AsyncSession = Depends(get_db)
):
    """
    修改api路径
    """
    if not new_path:
        return await response_code.resp_400(message='路径不能为空')

    return await crud.update_case_path(db=db, detail_id=detail_id, new_path=new_path)
