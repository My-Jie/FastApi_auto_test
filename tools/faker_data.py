#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: faker_data.py
@Time: 2022/9/5-17:32
"""

import time
import random
import string
from faker import Faker


class FakerData:

    def __init__(self, *_):
        self._faker = Faker(locale='zh_CN')

    def _name(self, *_) -> str:
        return self._faker.name_female()

    def _ssn(self, *_) -> int:
        return self._faker.ssn(min_age=18, max_age=50)

    def _phone_number(self, *_) -> int:
        return self._faker.phone_number()

    def _credit_card_number(self, *_) -> int:
        return self._faker.credit_card_number()

    def _city(self, *_) -> str:
        return self._faker.city()

    def _address(self, *_) -> str:
        return self._faker.address()[:-7]

    @staticmethod
    def _random_int(*args) -> int:
        length = int(args[0]) if int(args[0]) <= 20 else 20
        i = [str(x) for x in range(1, 9)]
        return int(''.join(random.sample(i, length)))

    @staticmethod
    def _time_int(*args) -> int:
        now_time = int(time.time())
        if isinstance(args, tuple):
            day = int(args[0])
        else:
            day = args
        if day == 0:
            return now_time * 1000

        if day == -1:
            return (now_time - 86400) * 1000

        if day == 1:
            return (now_time + 86400) * 1000

        if day == -2:
            return int(time.mktime(
                time.strptime(time.strftime('%Y-%m-%d', time.localtime(now_time - 86400)), '%Y-%m-%d'))) * 1000

        if day == 2:
            return int(time.mktime(
                time.strptime(time.strftime('%Y-%m-%d', time.localtime(now_time + 86400)), '%Y-%m-%d')) + 86399) * 1000

        return now_time * 1000

    def _time_str(self, *args) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._time_int(args[0]) // 1000))

    @staticmethod
    def _random_lower(*args) -> str:
        length = int(args[0]) if int(args[0]) <= 20 else 20
        return ''.join(random.sample(string.ascii_lowercase, length))

    @staticmethod
    def _random_upper(*args) -> str:
        length = int(args[0]) if int(args[0]) <= 20 else 20
        return ''.join(random.sample(string.ascii_uppercase, length))

    @staticmethod
    def _random_letter(*args) -> str:
        length = int(args[0]) if int(args[0]) <= 20 else 20
        return ''.join(random.sample(string.ascii_letters, length))

    @staticmethod
    def _random_cn(*args) -> str:
        length = int(args[0]) if int(args[0]) <= 20 else 20
        cn = [chr(random.randint(0x4e00, 0x9fbf)) for _ in range(100)]
        return ''.join(random.sample(cn, length))

    @staticmethod
    def _compute(*args) -> (int, float, str):
        try:
            return round(eval(args[0]), 6)
        except SyntaxError:
            return args[0]

    def faker_data(self, func: str, param: (int, str)) -> (str, int):
        """
        :param func:
        :param param:
        :return:
        """
        func_dict = {
            'name': self._name,
            'ssn': self._ssn,
            'phone_number': self._phone_number,
            'credit_card_number': self._credit_card_number,
            'city': self._city,
            'address': self._address,
            'random_int': self._random_int,
            'random_lower': self._random_lower,
            'random_upper': self._random_upper,
            'random_letter': self._random_letter,
            'random_cn': self._random_cn,
            'compute': self._compute,
            'time_int': self._time_int,
            'time_str': self._time_str,
        }
        if func_dict.get(func):
            return func_dict[func](param)


if __name__ == '__main__':
    f = FakerData()
    a = f.faker_data('random_int', 2)
    print(a)
