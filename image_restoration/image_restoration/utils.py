# -*- coding = utf-8 -*-
# @Time : 2022/3/22 0:28
# @Author : 王栋
# @File : utils.py
# Software : PyCharm
# 密码加密算法
import hashlib
import socket
from django.http import JsonResponse
from datetime import datetime
from image_restoration import settings


# 密码加密算法
def encryption(password: str):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


# 不传递identity默认跳过删除cookie，传递identity则根据identity检验是否需要删除cookie
def gen_response(code: int, data, identity=None):
    response = JsonResponse({
        'code': code,
        'data': data
    }, status=code)
    response["Access-Control-Allow-Origin"] = settings.front_url
    response["Access-Control-Allow-Credentials"] = "true"
    if identity is not None and identity <= 0:
        response.delete_cookie("username")
        response.delete_cookie("id")
        response.delete_cookie("identity")
    return response


def change_to_int_list(str_list: list):
    data = []
    for i in str_list:
        if i:
            data.append(int(i))
    return data


def change_to_float_list(str_list: list):
    data = []
    for i in str_list:
        if i:
            data.append(float(i))
    return data


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_datetime(get_timestamp: float):
    if get_timestamp < 1E10:
        return datetime.fromtimestamp(get_timestamp)
    else:
        return datetime.fromtimestamp(get_timestamp / 1000)


def catch_error(fn):
    def wrap(request, *args, **kwargs):
        try:
            response = fn(request, *args, **kwargs)
            if isinstance(response, JsonResponse):
                return response
            else:
                return gen_response(412, "your response is not a JsonResponse but: " + str(response))
        except Exception as e:
            print(e)
            return gen_response(411, str(e))

    return wrap


def lock(obj):
    if obj.modify_lock == 0:
        obj.modify_lock = 1
        obj.save()
        return 0
    else:
        return -1


def unlock(obj):
    obj.modify_lock = 0
    obj.save()
