#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
@Author: Kobayasi
@File: read_swagger.py
@Time: 2023/3/27-10:21
"""

import copy


class ReadSwagger:

    def __init__(self, host):
        self.type_dict = {
            'string': '',
            'integer': 0,
            'number': 0,
            'boolean': False,
            'array': [],
            'object': {}
        }
        self.temp = {
            'number': 0,
            'host': host,
            'path': '',
            'code': 200,
            'method': 'GET',
            'params': {},
            'json_body': 'json',
            'data': {},
            'file': False,
            'file_data': [],
            'headers': {},
            'response': {},
        }

    def header(self, swagger: dict):
        """
        处理swagger数据
        :param swagger:
        :return:
        """
        temp_list = []
        num = 0
        for path, v in swagger['paths'].items():
            for k_, v_ in v.items():
                temp = copy.deepcopy(self.temp)
                temp['path'] = path
                temp['number'] = num
                temp['method'] = k_.upper()
                if v_.get('consumes'):
                    temp['headers'] = {"Content-Type": v_.get('consumes')[0]}

                if v_.get('parameters'):
                    for x in v_.get('parameters'):
                        if '.' in x['name']:
                            continue

                        parameters = self._parameters_type(x, swagger['definitions'])
                        if x['in'] == 'query':
                            temp['params'] = {**temp['params'], **parameters}
                        if x['in'] == 'body':
                            temp['data'] = {**temp['data'], **parameters}

                if v_.get('responses'):
                    temp['response'] = self._responses_type(v_['responses']['200'], swagger['definitions'])

                temp['json_body'] = 'body' if temp['params'] else 'json'
                temp_list.append(temp)
                num += 1

        return temp_list

    def _header_definitions(self, parameters: dict, definitions_: dict):
        """
        处理引用数据
        :param parameters:
        :param definitions_:
        :return:
        """
        original_dict = {}

        def inter(params):
            target = {}
            for k, v in params.items():
                if v.get('type', '_') == 'array':
                    if v['items'].get('type'):
                        target[k] = [self.type_dict[v['items']['type']]]
                    else:
                        if definitions_[v['items']['originalRef']].get('properties'):

                            # 限制深度
                            if original_dict.get(v['items']['originalRef']):
                                original_dict[v['items']['originalRef']] += 1
                            else:
                                original_dict[v['items']['originalRef']] = 1
                            if original_dict[v['items']['originalRef']] >= 2:
                                continue

                            target[k] = [inter(definitions_[v['items']['originalRef']]['properties'])]
                        else:
                            target[k] = self.type_dict[v['type']]
                else:
                    if v.get('type'):
                        if v.get('type'):
                            target[k] = self.type_dict[v['type']]
                        else:
                            target[k] = ''
                    else:
                        if definitions_[v['originalRef']].get('properties'):

                            # 限制深度
                            if original_dict.get(v['originalRef']):
                                original_dict[v['originalRef']] += 1
                            else:
                                original_dict[v['originalRef']] = 1
                            if original_dict[v['originalRef']] >= 2:
                                continue

                            target[k] = inter(definitions_[v['originalRef']]['properties'])
                        else:
                            if v.get('type'):
                                target[k] = self.type_dict[v['type']]
                            else:
                                target[k] = ''
            return target

        return inter(parameters)

    def _parameters_type(self, parameters: dict, definitions: dict):
        """
        判断请求参数的数据类型
        :param parameters:
        :param definitions:
        :return:
        """

        if parameters['in'] == 'query':
            if parameters.get('type'):
                return {parameters['name']: self.type_dict.get(parameters['type'])}
            else:
                return {parameters['name']: self.type_dict.get(parameters['items']['type'])}

        if parameters['in'] == 'body':
            if parameters['schema'].get('type'):
                return {parameters['name']: self.type_dict.get(parameters['schema']['type'])}
            else:
                return {
                    parameters['name']: self._header_definitions(
                        definitions[parameters['schema']['originalRef']]['properties'],
                        definitions
                    )
                }

    def _responses_type(self, responses: dict, definitions: dict):
        """
        判断响应参数的数据类型
        :param responses:
        :param definitions:
        :return:
        """

        if not responses.get('schema'):
            return {}

        if responses['schema'].get('type'):
            return {}

        return self._header_definitions(
            definitions[responses['schema']['originalRef']]['properties'],
            definitions
        )
