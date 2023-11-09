# -*- coding = utf-8 -*-
# @Time : 2022/4/9 18:46
# @Author : 王栋
# @File : utils.py
# Software : PyCharm
import threading
import time
from exhibit.models import Exhibit
from picture.models import Picture, Image
from image_restoration import settings
from user.models import AvatarImage, User


def test_tags(obj, search_tags):
    obj_tags = [tag.name for tag in obj.tags.all()]
    for tag in search_tags:
        if tag not in obj_tags:
            return False
    return True


# 返回picture对象的修复步骤中的最后一张照片,如果没有修复步骤就返回原图,如果picture为空则返回picture的default照片
def get_pic_url(obj, default=0):
    if isinstance(obj, Picture):
        picture = obj
    elif isinstance(obj, Exhibit):
        picture = obj.pictures.first()
        if picture is None:
            return settings.default_exhibit_url
    else:
        if default == 0:
            return settings.default_picture_url
        else:
            return settings.default_exhibit_url
    url = picture.pic.url
    for step in picture.repairstep_set.all():
        if settings.default_repair_name not in step.pic.url:
            url = step.pic.url
    return url


# 将图片的url转化为本地的地址
def change_http_url_to_local(file_path: str):
    return file_path.replace(settings.back_url, ".")


def save_pic(pic_path, obj):
    try:
        with open(pic_path, "rb") as file:
            if obj.img is None:
                if isinstance(obj, Picture):
                    obj.img = Image.objects.create()
                elif isinstance(obj, User):
                    obj.img = AvatarImage.objects.create()
            obj.img.img = file.read()
            obj.img.save()
            obj.save()
        return ""
    except Exception as exp:
        return str(exp) + "; "


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(*self.args)

    def get_result(self):
        # 线程不结束,返回值为None
        try:
            return self.result
        except Exception:
            return None


# 为了限制真实请求时间或函数执行时间的装饰器
def limit_decor(limit_time):
    """
    :param limit_time: 设置最大允许执行时长,单位:秒
    :return: 未超时返回被装饰函数返回值,超时则返回 None
    """

    def functions(func):
        # 执行操作
        def run(*params):
            this_func = MyThread(target=func, args=params)
            # 主线程结束(超出时长),则线程方法结束
            this_func.setDaemon(True)
            this_func.start()
            # 计算分段沉睡次数
            sleep_num = int(limit_time // 1)
            sleep_nums = round(limit_time % 1, 1)
            # 多次短暂沉睡并尝试获取返回值
            for i in range(sleep_num):
                time.sleep(1)
                info = this_func.get_result()
                if info is not None:
                    return info
            time.sleep(sleep_nums)
            # 最终返回值(不论线程是否已结束)
            if this_func.get_result() is not None:
                return this_func.get_result()
            else:
                return -1  # 超时返回  可以自定义

        return run

    return functions
