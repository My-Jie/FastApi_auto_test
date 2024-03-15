#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
@File    ：diff_dict.py
@IDE     ：PyCharm 
@Author  ：Kobayasi
@Date    ：2024/2/28 10:35 
"""

import json


async def compare_data(new_data, old_data, path=""):
    """
    比较两个数据的差异
    :param new_data: 数据1
    :param old_data: 数据2
    :param path: 路径
    :return: 返回两个数据的差异
    """
    # 用于保存结果的字典
    results = {
        "added": [],
        "removed": [],
        "value_changed": [],
        "key_changed": []
    }

    if isinstance(new_data, dict) and isinstance(old_data, dict):
        new_keys, old_keys = set(new_data.keys()), set(old_data.keys())
        added_keys = new_keys - old_keys
        removed_keys = old_keys - new_keys
        common_keys = new_keys & old_keys

        for key in added_keys:
            # results["added"].append((path + str(key), new_data[key]))
            results["added"].append({'path': path + str(key), 'value': new_data[key], 'replace': False})

        for key in removed_keys:
            # results["removed"].append((path + str(key), old_data[key]))
            results["removed"].append({'path': path + str(key), 'value': old_data[key], 'replace': False})

        for key in common_keys:
            new_path = f"{path}{key}."
            compare_result = await compare_data(new_data[key], old_data[key], new_path)
            for k in results.keys():
                results[k].extend(compare_result[k])

    elif isinstance(new_data, list) and isinstance(old_data, list):
        # 比较列表中的元素
        longer, shorter = (new_data, old_data) if len(new_data) > len(old_data) else (old_data, new_data)
        for i in range(len(longer)):
            if i >= len(shorter):  # 新增或删除的元素
                operation = "added" if longer is new_data else "removed"
                # results[operation].append((f"{path}[{i}]", longer[i]))
                results[operation].append({'path': f"{path}[{i}]", 'value': longer[i], 'replace': False})
            else:  # 对比同一位置的元素
                new_path = f"{path}[{i}]."
                compare_result = await compare_data(new_data[i], old_data[i], new_path)
                for k in results.keys():
                    results[k].extend(compare_result[k])
    elif new_data != old_data:  # 值改变
        # if isinstance(old_data, str):
        #     replace = True if '{{' not in old_data and '}}' not in old_data else False
        # else:
        #     replace = False
        # results["value_changed"].append((path[:-1], (old_data, new_data, replace)))
        results["value_changed"].append(
            {'path': path[:-1], 'old_value': old_data, 'new_value': new_data, 'replace': False}
        )

    return results


async def apply_changes(old_data, changes: dict):
    # 应用新增的字段
    for added in changes.get('added', []):
        keys, value = added['path'].split('.'), added['value']
        current = old_data
        for key in keys[:-1]:
            if key[1:-1].isdigit():  # list索引
                current = current[int(key[1:-1])]
            else:  # dict键
                current = current[key]
        if keys[-1].isdigit():
            current.append(value)  # 对于list，添加新元素
        else:
            current[keys[-1]] = value  # 对于dict，添加新键值对

    # 应用移除的字段
    for removed in changes.get('removed', []):
        keys = removed['path'].split('.')
        current = old_data
        for key in keys[:-1]:
            if key[1:-1].isdigit():
                current = current[int(key[1:-1])]
            else:
                current = current[key]
        if keys[-1].isdigit():
            del current[int(keys[-1])]  # 删除列表中的元素
        else:
            del current[keys[-1]]  # 删除字典中的键值对

    # 应用值变更
    for value_changed in changes.get('value_changed', []):
        keys, value = value_changed['path'].split('.'), value_changed['new_value']  # 获取新值
        current = old_data
        for key in keys[:-1]:
            if key[1:-1].isdigit():
                current = current[int(key[1:-1])]
            else:
                current = current[key]
        if keys[-1][1:-1].isdigit():
            current[int(keys[-1][1:-1])] = value  # 更新列表中的值
        else:
            current[keys[-1]] = value  # 更新字典中的值

    return old_data
