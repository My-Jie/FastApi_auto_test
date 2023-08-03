#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: My_Jie
@File: my_sql.py
@Time: 2021/1/12-14:12
"""

# from tools import logger
import aiomysql.sa as aio_sa


class AsyncMySql:

    def __init__(self, kwargs):
        """
        数据库上下文关联器
        :param kwargs:
        """
        self.kwargs = kwargs
        self.engine = None
        self.conn = None

    async def __aenter__(self):
        self.engine = await aio_sa.create_engine(**self.kwargs)
        self.conn = await self.engine.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()
        self.engine.close()

    async def select(self, sql):
        try:
            result = await self.conn.execute(sql)
            # logger.info(f"SQL查询成功：{sql}")
        except Exception:
            # logger.error(f"SQL查询失败：{sql}, error:{e}")
            return []
        return await result.fetchall()
