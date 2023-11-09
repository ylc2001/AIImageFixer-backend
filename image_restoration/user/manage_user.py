# -*- coding = utf-8 -*-
# @Time : 2022/3/21 14:30
# @Author : 王栋
# @File : manage_user.py
# Software : PyCharm
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from user.check_login import check_admin, update_freeze, check_user
from image_restoration.utils import gen_response


# 批量查找用户
@csrf_exempt
@check_admin
@csrf_exempt
def search_user(request):
    if request.method == "GET":
        # 检查数据库内的封禁用户是否到期解封
        update_freeze()

        # 获取用户名和查找类型
        try:
            # username可以不传
            username = request.GET.get("text")
            # 类型是必须穿的参数而且必须为整数，0：未审批用户 1：普通用户 2：封禁用户
            return_type = int(request.GET['type'])
        except Exception as e:
            return gen_response(400, str(e))
        # 根据username先做一次筛选
        if username:
            users = User.objects.filter(username__contains=username)
        else:
            users = User.objects.all()

        # 根据用户类型做二次查找
        if return_type == 0:
            users = users.filter(is_register=True)
            data = [{"username": user.username, "id": user.id} for user in users]
            return gen_response(200, data)
        elif return_type == 1:
            users = users.filter(is_active=True, is_register=False, is_admin=False, is_superuser=False)
            data = [{"username": user.username, "id": user.id} for user in users]
            return gen_response(200, data)
        elif return_type == -1:
            users = users.filter(is_active=False)
            data = [{"username": user.username, "id": user.id} for user in users]
            return gen_response(200, data)

        # return_type不存在或者为其他值
        else:
            return gen_response(402, "请提交正确的表单数据")

    # 发送其他类型的请求
    else:
        return gen_response(400, "无法接受该请求")


# 删除一个用户
@csrf_exempt
@check_admin
def delete_user(request):
    # 尝试从数据库中获取待删除用户的信息
    if request.method == "POST":
        try:
            delete_id = int(request.POST['id'])
            delete_obj = User.objects.get(id=delete_id)

        # 如果没有则说明表单提交错误
        except Exception as e:
            return gen_response(400, str(e))

        # 验证待删除用户的身份
        delete_identity = check_user(delete_obj)

        # 要删除的普通用户(封禁/未封禁)或者待审核用户
        if 1 >= delete_identity >= -1:
            delete_obj.delete()
            return gen_response(200, "删除成功")
        elif delete_identity == -2 or delete_identity == 2:
            if request.session["identity"] == 3:
                delete_obj.delete()
                return gen_response(200, "删除成功")
            else:
                return gen_response(402, "您没有删除该用户的权限")
        else:
            return gen_response(403, "您没有删除该用户的权限")
    else:
        return gen_response(405, "method error")


# 封禁操作接受用户id和操作类型
# ToDo 添加封禁时间的操作
@csrf_exempt
@check_admin
def banned_user(request):
    if request.method == "POST":
        # 提取表单中的信息
        try:
            banned_id = int(request.POST["id"])
            banned_type = int(request.POST["type"])
            # 尝试从数据库中获取该用户并校验被封禁用户的身份
            user = User.objects.get(id=banned_id)
        except Exception as e:
            return gen_response(400, str(e))

        banned_identity = check_user(user)
        # 封禁操作
        if banned_type == 0:
            if banned_identity == 1:
                user.is_active = False
                user.freeze = True
                user.save()
                return gen_response(200, "您已成功封禁该用户")
            elif banned_identity == 2:
                if request.session["identity"] == 3:
                    user.is_active = False
                    user.freeze = True
                    user.save()
                    return gen_response(200, "您已成功封禁该用户")
                else:
                    return gen_response(402, "您没有权限封禁该用户!")
            elif banned_identity == 3:
                return gen_response(403, "您没有权限封禁该用户")
            else:
                return gen_response(405, "该用户处于封禁状态或尚未注册,封禁操作无法进行!")
        # 解封操作
        elif banned_type == 1:
            if banned_identity == -1:
                user.is_active = True
                user.freeze = False
                user.save()
                return gen_response(200, "您已成功解封该用户")
            elif banned_identity == -2:
                if request.session["identity"] == 3:
                    user.is_active = True
                    user.freeze = False
                    user.save()
                    return gen_response(200, "您已成功解封该用户")
                else:
                    return gen_response(406, "您没有权限解封该用户")
            else:
                return gen_response(407, "该用户无需解封!")

    # 发起的并非post请求
    else:
        return gen_response(408, "请提交正确的请求")


# 审批通过的用户，其中管理员不能审批申请管理员的用户
@csrf_exempt
@check_admin
def review_user(request):
    if request.method == "POST":
        try:
            review_id = int(request.POST["id"])
            user = User.objects.get(id=review_id)

        except Exception as e:
            return gen_response(400, str(e))

        identity = check_user(user)

        if identity == 0:
            if user.is_admin:
                if request.session["identity"] == 3:
                    user.is_register = False
                    user.save()
                    return gen_response(200, "审批成功!")
                else:
                    return gen_response(402, "您没有权限审批该用户")
            else:
                user.is_register = False
                user.save()
                return gen_response(200, "审批成功!")
        else:
            return gen_response(403, "该用户已注册,无法二次审批")
    # 发送不同类型的请求
    else:
        return gen_response(405, "请发送正确的请求!")
