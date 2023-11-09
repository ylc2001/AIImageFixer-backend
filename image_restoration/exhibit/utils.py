# -*- coding = utf-8 -*-
# @Time : 2022/4/23 15:29
# @Author : 王栋
# @File : utils.py
# Software : PyCharm
from image_restoration import settings


def get_style_list(style: int):
    """
    接受数据库中存储的展览的样式数据
    将其转化为样式列表后返回
    """
    style_list = []
    if style == 0:
        return [0]
    while style != 0:
        style_list.append(style % settings.style_num)
        style //= settings.style_num
    return style_list


def save_style_list(style_str: str):
    """
    接受一个用逗号隔开的int列表
    将其转化为对应的进制数返回
    """
    style_str_list = style_str.split(",")
    style_int_list = []
    style = 0
    for i in style_str_list:
        if i:
            style_step = int(i)
        else:
            continue
        if 0 <= style_step < settings.style_num:
            style_int_list.append(style_step)
    if len(style_int_list) > settings.style_num or len(style_int_list) == 0:
        return -1
    style_int_list.sort()
    for i in range(len(style_int_list)):
        style_step = style_int_list[i]
        style += style_step * settings.style_num ** i
    return style
