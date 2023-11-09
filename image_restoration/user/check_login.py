# -*- coding = utf-8 -*-
# @Time : 2022/3/20 23:04
# @Author : 王栋
# @File : check_login.py
# Software : PyCharm
from django.utils import timezone
from user.models import User
from image_restoration.utils import gen_response


# 被封禁的管理员：返回-2
# 被封禁的用户：返回-1
# 未注册（注册未审批的）游客：返回0
# 普通用户：返回1
# 管理员：返回2
# 超级管理员：返回3
# 如果是负数记得删cookie


# 该方法通过request携带的cookie和session校验用户身份
# 返回{"identity":int,"user":User}
def check_identity(request):
    if 'id' not in request.session:
        # 当没有session_id的时候尝试从cookie中获取用户信息
        try:
            c_username = request.COOKIES.get('username')
            c_id = int(request.COOKIES.get('id')) if request.COOKIES.get("id") else None
        except Exception as e:
            return {"identity": 0, "user": None, "error": str(e)}

        # 如果仍然没有则为游客登录
        if not c_username or not c_id:
            request.session.flush()
            return {"identity": 0, "user": None}
        # 有cookie没session
        else:
            try:
                user = User.objects.get(id=c_id)
            except Exception as e:
                # 不存在该用户
                request.session.flush()
                return {"identity": 0, "user": None, "error": str(e)}
            identity = check_user(user)
            if identity >= 1:
                # 写回session中
                request.session['username'] = c_username
                request.session['id'] = c_id
                request.session["identity"] = identity
                return {"identity": identity, "user": user}
            else:
                request.session.flush()
                return {"identity": identity, "user": user}
    else:
        c_id = request.session['id']
        try:
            user = User.objects.get(id=c_id)
        except Exception as e:
            # 不存在该用户
            request.session.flush()
            return {"identity": 0, "user": None, "error": str(e)}
        identity = check_user(user)
        if identity >= 1:
            request.session["identity"] = identity
            return {"identity": identity, "user": user}
        else:
            request.session.flush()
            return {"identity": identity, "user": user}


# 装饰器，如果不是管理员/超级用户直接返回401
def check_admin(fn):
    def wrap(request, *args, **kwargs):
        identity = check_identity(request)["identity"]
        if identity >= 2:
            return fn(request, *args, **kwargs)
        else:
            return gen_response(401, "您没有管理员权限", identity)

    return wrap


# 装饰器，如果不是普通用户直接返回401
def check_average_user(fn):
    def wrap(request, *args, **kwargs):
        identity = check_identity(request)["identity"]
        if identity == 1:
            return fn(request, *args, **kwargs)
        else:
            return gen_response(401, "您不是普通用户", identity)

    return wrap


# 装饰器，如果非注册直接返回401,用于点赞和评论
def check_comment_and_like(fn):
    def wrap(request, *args, **kwargs):
        identity = check_identity(request)["identity"]
        if identity >= 1:
            return fn(request, *args, **kwargs)
        else:
            return gen_response(401, "您还没有注册", identity)

    return wrap


# 装饰器,检验用户是否为未登录的身份
def check_undefined(fn):
    def wrap(request, *args, **kwargs):
        temp_dic = check_identity(request)
        identity = temp_dic["identity"]
        user = temp_dic["user"]
        if identity == 0:
            if not user:
                return fn(request, *args, **kwargs)
            else:
                return gen_response(401, "尚未审核通过的用户", identity)
        else:
            return gen_response(401, "请先注销", identity)

    return wrap


# 装饰器,检验用户是否未被封禁
def check_unfreeze(fn):
    def wrap(request, *args, **kwargs):
        identity = check_identity(request)["identity"]
        if identity >= 0:
            return fn(request, *args, **kwargs)
        else:
            return gen_response(401, "请先注销", identity)

    return wrap


# 该方法通过传入的user对象校验身份
def check_user(user: User):
    """
    传入user对象
    返回int数据
    """
    is_admin = user.is_admin
    is_root = user.is_superuser
    is_register = user.is_register
    is_active = user.is_active
    freeze = user.freeze
    free_date = user.free_date
    if is_register:
        # 审批未通过的用户，相当于游客，返回0
        return_result = 0
    elif is_admin:
        # 管理员返回2
        return_result = 2
    elif is_root:
        # 超级管理员返回3
        return_result = 3
    else:
        # 普通用户返回1
        return_result = 1
    if is_active:
        return return_result
    elif freeze:
        return -return_result
    else:
        if timezone.now() > free_date:
            user.is_active = True
            user.freeze_date = None
            user.save()
            return return_result
        else:
            return -return_result


def update_freeze():
    """
    更新所有被封禁的用户
    对其中的每个用户进行校验，查看是否可以解除封禁
    如果可以就修改数据库中的内容
    """
    users = User.objects.filter(is_active=False)
    for user in users:
        # 并非永久封禁，检测封禁是否到期
        if not user.freeze and user.free_date < timezone.now():
            user.is_active = True
            user.free_date = None
            user.save()
