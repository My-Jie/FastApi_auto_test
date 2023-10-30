#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: assert_case.py
@Time: 2023/10/27-14:34
"""

from typing import Any


class AssertCase:
    """
    断言接口测试用例
    """

    @classmethod
    async def assert_case(
            cls,
            k: str,
            compare: str,
            expect: Any,
            actual: Any,
            result: list
    ) -> bool:
        """
        断言
        :param k: 校验字段
        :param compare: 比较符
        :param expect: 预期值
        :param actual: 实际值
        # :param is_fail: 是否失败
        :param result: 校验结果集
        :return:
        """
        assert_dict = {
            "<": cls.assert_less,
            "<=": cls.assert_less_equal,
            "==": cls.assert_equal,
            "!=": cls.assert_not_equal,
            ">=": cls.assert_greater_equal,
            ">": cls.assert_greater,
            "in": cls.assert_in,
            "not in": cls.assert_not_in,
            "notin": cls.assert_not_in,
            "!in": cls.assert_in_,
            "!not in": cls.assert_not_in_,
            "!notin": cls.assert_not_in_,
        }

        is_fail = assert_dict.get(compare)(actual, expect)
        result.append(
            {
                'key': k,
                'actual': actual,
                'compare': compare,
                'expect': expect,
                'is_fail': 'fail' if is_fail else 'pass'
            }
        )

        return is_fail

    @staticmethod
    def assert_less(actual, expect) -> bool:
        # 小于
        return False if actual < expect else True

    @staticmethod
    def assert_less_equal(actual, expect) -> bool:
        # 小于等于
        return False if actual <= expect else True

    @staticmethod
    def assert_equal(actual, expect) -> bool:
        # 等于
        return False if actual == expect else True

    @staticmethod
    def assert_not_equal(actual, expect) -> bool:
        # 不等于
        return False if actual != expect else True

    @staticmethod
    def assert_greater_equal(actual, expect) -> bool:
        # 大于等于
        return False if actual >= expect else True

    @staticmethod
    def assert_greater(actual, expect) -> bool:
        # 大于
        return False if actual > expect else True

    @staticmethod
    def assert_in(actual, expect) -> bool:
        # 包含
        return False if actual in str(expect) else True

    @staticmethod
    def assert_not_in(actual, expect) -> bool:
        # 不包含
        return False if actual not in str(expect) else True

    @staticmethod
    def assert_in_(actual, expect) -> bool:
        # 包含
        return False if expect in str(actual) else True

    @staticmethod
    def assert_not_in_(actual, expect) -> bool:
        # 包含
        return False if expect not in str(actual) else True
