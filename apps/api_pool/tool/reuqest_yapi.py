#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: reuqest_yapi.py
@Time: 2022/8/29-12:51
"""

import re
import json
import aiohttp
from sqlalchemy.orm import Session
from tools import logger
from tools import get_cookie
from apps.api_pool import crud
from apps.api_pool import schemas


class YApi:

    def __init__(self, host: str):
        self._host = host
        self._headers = {}
        self._group = []
        self._sess = aiohttp.client.ClientSession()

    async def login(self, email: str, password: str, api: str = '/api/user/login') -> bool:
        """
        登录接口
        :param api:
        :param email:
        :param password:
        :return:
        """
        data = {
            'email': email,
            'password': password
        }

        async with self._sess.post(self._host + api, json=data) as res:
            if res.status != 200:
                logger.error('YApi登录失败')
                return False

        self._headers = {
            'cookie': await get_cookie(rep_type='aiohttp', response=res)
        }
        logger.info('YApi登录成功')
        return True

    async def get_project_list(self, api: str = '/api/group/list'):
        """
        获取项目的基本信息
        :return:
        """

        async with self._sess.get(self._host + api, headers=self._headers) as res:
            res_json = await res.json()
            if res_json['errmsg'] != '成功！':
                return

        self._group = [x for x in res_json['data'] if x['group_name'] != '个人空间']

    async def get_project_sub_list(self, group_id: int, page: int = 1, limit: int = 10, api: str = '/api/project/list'):
        """
        循环项目，获取项目列表
        :param group_id:
        :param page:
        :param limit:
        :param api:
        :return:
        """
        project_params = {
            'group_id': group_id,
            'page': page,
            'limit': limit
        }
        async with self._sess.get(self._host + api, params=project_params, headers=self._headers) as res:
            res_json = await res.json()
            return res_json['data']['list']

    async def get_interface_list(self, pro_id: int, page: int = 1, limit: int = 100, api: str = '/api/interface/list'):
        """
        获取页面上，小项目的api列表
        :param pro_id: 页面项目的id
        :param page:
        :param limit:
        :param api:
        :return:
        """
        interface_params = {
            'project_id': pro_id,
            'page': page,
            'limit': limit,
        }
        async with self._sess.get(self._host + api, params=interface_params, headers=self._headers) as res:
            res_json = await res.json()
            return res_json['data']['list']

    async def get_interface_api(self, api_id: int, api: str = '/api/interface/get'):
        """
        获取单个接口的信息
        :param api_id:
        :param api:
        :return:
        """
        interface_get_params = {
            'id': api_id
        }
        async with self._sess.get(self._host + api, params=interface_get_params, headers=self._headers) as res:
            res_json = await res.json()
            return res_json['data']

    async def header_all_data(self, db: Session):
        """
        全量下载数据
        :return:
        """
        pro = []
        await self.get_project_list()
        # 第一层循环项目
        for group in self._group:
            project_list = await self.get_project_sub_list(group['_id'])
            # 第二层循环项目列表
            for project in project_list:
                project_info = {
                    'group_id': group['_id'],
                    'group_name': group['group_name'],
                    'group_desc': group['group_desc'],
                    'project_id': project['_id'],
                    'project_name': project['name'],
                }
                yai_info = await crud.create_api_project(db=db, data=schemas.YApi(**project_info))
                interface_list = await self.get_interface_list(project['_id'])
                # 第三层循环获取api数据
                for api in interface_list:
                    interface_api = await self.get_interface_api(api['_id'])
                    api_pool = await self._header_api_pool(interface_api, project['_id'])
                    await crud.create_api_pool(db=db, data=schemas.YApiData(**api_pool))
                pro.append(await crud.update_api_project(db=db, yai_id=yai_info.id, api_count=len(interface_list)))
        await self._sess.close()
        return pro

    async def header_project_data(self, project_id: int, db: Session):
        """
        按项目名称更新数据
        :param project_id:
        :param db:
        :return:
        """
        interface_list = await self.get_interface_list(project_id)
        api_list = []
        for api in interface_list:
            interface_api = await self.get_interface_api(api['_id'])
            api_pool = await self._header_api_pool(interface_api, project_id)
            api_list.append(await crud.create_api_pool(db=db, data=schemas.YApiData(**api_pool)))
        await self._sess.close()
        return api_list

    async def header_api_data(self, api_id: int, project_id: int, db: Session):
        """
        更新单个用例数据
        :param api_id:
        :param project_id:
        :param db:
        :return:
        """
        interface_api = await self.get_interface_api(api_id)
        api_pool = await self._header_api_pool(interface_api, project_id)
        api_info = await crud.create_api_pool(db=db, data=schemas.YApiData(**api_pool))
        await self._sess.close()
        return api_info

    @staticmethod
    async def _header_api_pool(interface_api: dict, project_id: int) -> dict:
        """
        处理api数据
        :param interface_api:
        :param project_id:
        :return:
        """
        if interface_api.get('req_body_type') == 'json':
            json_body = 'json'
            req_data = json.loads(interface_api.get('req_body_other', "{}"))
        elif interface_api.get('req_body_type') == 'form':
            json_body = 'body'
            req_data = interface_api['req_body_form']
        else:
            json_body = 'json'
            if interface_api.get(''):
                req_data = re.sub('\n', '', interface_api['req_body_other'])
                req_data = json.loads(req_data)
            else:
                req_data = {}

        api_pool = {
            'api_id': interface_api['_id'],
            'project_id': project_id,
            'title': interface_api['title'],
            'path': interface_api['path'],
            'req_headers': interface_api.get('req_headers'),
            'method': interface_api['method'],
            'req_params': interface_api['req_query'],
            'json_body': json_body,
            'req_data': req_data
        }
        return api_pool
