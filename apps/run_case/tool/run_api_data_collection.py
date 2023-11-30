#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：run_api_data_collection.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2023/11/27 20:01 
"""

import time
from apps.case_service.tool import js_count


def api_detail(
        number,
        case_id,
        case_data,
        temp_data,
        res,
        res_json,
        response_time,
        request_info,
        check,
        actual,
        config,
        is_fail,
        result,
        case_response
):
    # 测试报告详情数据
    return {
        'number': number,
        'status': 'pass' if not is_fail else 'fail',
        'method': temp_data.method,
        'host': temp_data.host,
        'path': case_data.path,
        'run_time': response_time,
        'request_info': request_info,
        'response_info': {
            'status_code': res.status,
            'response': res_json,
            'response_headers': dict(res.headers)
        },
        'expect_info': check,
        'actual_info': actual,
        'jsonpath_info': js_count(
            case_id=case_id,
            case_list=[case_data],
            temp_list=[temp_data],
            run_case=case_response
        ),
        'conf_info': config,
        'other_info': {
            'description': case_data.description if case_data.description else '--',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
            'file': True if temp_data.file else False,
            'assert_info': result
        }
    }


class ApiReport:

    def __init__(self, total_api):
        self.api_report = {
            "case_id": 0,
            "is_fail": False,
            "run_number": 0,
            "run_api": 0,
            "total_api": total_api,
            "initiative_stop": False,
            "fail_stop": False,
            "success": 0,
            "fail": 0,
            "total_time": 0,
            "max_time": 0,
            "avg_time": 0,
        }

    def report(
            self,
            case_id: int,
            is_fail: bool,
            response_time: float,
            config: dict,
            all_is_fail: bool,

    ):
        self.api_report['success' if not is_fail else 'fail'] += 1
        self.api_report['run_api'] += 1
        self.api_report['total_time'] += response_time
        if response_time > self.api_report['max_time']:
            self.api_report['max_time'] = response_time
        self.api_report['fail_stop'] = config.get('fail_stop', False)
        self.api_report['initiative_stop'] = config.get('stop', False)
        self.api_report['case_id'] = case_id
        self.api_report['is_fail'] = all_is_fail
        self.api_report['avg_time'] = self.api_report['total_time'] / self.api_report['run_api']


class CaseStatus:

    def __init__(self, case_id: int, total: int):
        self.case_status = {
            'success': 0,
            'fail': 0,
            'case_id': case_id,
            'total': total,
            'run': True
        }

    def status(
            self,
            num: int,
            number: int,
            status_code: int,
            response_time: float,
            is_fail: bool,
            config: dict,
            request_info: dict,
            res_json: dict,
            check: dict,
            result: dict,
            files: list,
            stop: bool
    ):
        self.case_status['number'] = number
        self.case_status['time'] = int(time.time() * 1000)
        self.case_status['time_str'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.case_status['status_code'] = status_code
        self.case_status['run_time'] = response_time
        self.case_status['is_fail'] = is_fail
        self.case_status['is_login'] = config['is_login']
        self.case_status['response_info'] = res_json
        self.case_status['sleep'] = config['sleep']
        self.case_status['expect'] = check
        self.case_status['actual'] = result
        self.case_status['continued'] = False if num < 1 else True
        self.case_status['stop'] = stop

        if num < 1:
            self.case_status['success' if not is_fail else 'fail'] += 1

        if files:
            request_info['data'] = [
                {
                    'name': file['name'],
                    'content_type': file['contentType'],
                    'filename': file['fileName']

                } for file in files
            ]

        self.case_status['request_info'] = request_info
