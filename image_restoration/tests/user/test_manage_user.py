# -*- coding = utf-8 -*-
# @Time : 2022/3/30 16:40
# @Author : 王栋
# @File : test_manage_user.py
# Software : PyCharm
from django.test import TestCase
from tests.utils import set_cookie, add_user_data


class TestUserManage(TestCase):
    # 初始化管理员和普通的用户用于测试
    def setUp(self):
        add_user_data(self)

    def test_search_user(self):
        def send_search_get(search_type: int = None, username: str = None):
            data = {}
            if search_type is not None:
                data["type"] = search_type
            if username:
                data["text"] = username
            return self.client.get("/user/search_user", data=data)

        # 测试普通用户查询用户
        set_cookie(self.client, self.ordinary_user)
        response = send_search_get(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试管理员不传递参数
        set_cookie(self.client, self.admin_user)
        response = send_search_get()
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试管理员不传递username
        set_cookie(self.client, self.admin_user)
        response = send_search_get(1)
        self.assertEqual(response.status_code, 200)

        # 测试管理员两个参数都传递
        # type:1
        response = send_search_get(1, "register")
        self.assertEqual(response.status_code, 200)
        # type:0
        response = send_search_get(0, "register")

        self.assertEqual(response.status_code, 200)
        # type:-1
        response = send_search_get(-1, "register")
        self.assertEqual(response.status_code, 200)

        # 测试传入错误的type:str/int(except 0, -1, 1)
        response = send_search_get("bad", "register")
        self.assertEqual(response.status_code, 400)

        response = send_search_get(-4, "register")
        self.assertEqual(response.status_code, 402)

    def test_delete_user(self):
        def send_delete_post(delete_id: int = None):
            data = {}
            if delete_id is not None:
                data["id"] = delete_id
            return self.client.post("/user/delete_user", data=data)

        # 测试非管理员请求
        set_cookie(self.client, self.ordinary_user)
        response = send_delete_post(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试管理员发送请求时不带id
        set_cookie(self.client, self.admin_user)
        response = send_delete_post()
        self.assertEqual(response.status_code, 400)

        # 测试管理员删除同等权限的管理员
        response = send_delete_post(self.admin_user.id)
        self.assertEqual(response.status_code, 402)

        # 测试管理员删除更高权限的用户
        response = send_delete_post(self.super_user.id)
        self.assertEqual(response.status_code, 403)

        # 测试管理员删除普通用户
        response = send_delete_post(self.ordinary_user.id)
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试超级管理员删除管理员
        set_cookie(self.client, self.super_user)
        response = send_delete_post(self.admin_user.id)
        self.assertEqual(response.status_code, 200)

        # 测试错误的请求方式
        response = self.client.get("/user/delete_user")
        self.assertEqual(response.status_code, 405)
        self.client.cookies.clear()

    def test_banned_user(self):
        def send_ban_post(banned_id: int = None, banned_type: int = None):
            data = {}
            if banned_id is not None:
                data["id"] = banned_id
            if banned_type is not None:
                data["type"] = banned_type
            return self.client.post("/user/banned_user", data=data)

        # 测试普通用户尝试封禁操作
        set_cookie(self.client, self.ordinary_user)
        response = send_ban_post(self.ordinary_user.id, 0)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试管理员不提交参数
        set_cookie(self.client, self.admin_user)
        response = send_ban_post()
        self.assertEqual(response.status_code, 400)

        # 测试管理员封禁同等权限的用户
        response = send_ban_post(self.admin_user.id, 0)
        self.assertEqual(response.status_code, 402)

        # 测试管理员封禁超级用户
        response = send_ban_post(self.super_user.id, 0)
        self.assertEqual(response.status_code, 403)

        # 测试管理员封禁普通用户
        response = send_ban_post(self.ordinary_user.id, 0)
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试超级用户封禁管理员
        set_cookie(self.client, self.super_user)
        response = send_ban_post(self.admin_user.id, 0)
        self.assertEqual(response.status_code, 200)

        # 测试超级用户封禁尚未注册的用户
        response = send_ban_post(self.freeze_user.id, 0)
        self.assertEqual(response.status_code, 405)
        self.client.cookies.clear()

        # 测试普通管理员解封普通用户
        set_cookie(self.client, self.other_admin_user)
        response = send_ban_post(self.ordinary_user.id, 1)
        self.assertEqual(response.status_code, 200)

        # 测试管理员解封同级管理员
        response = send_ban_post(self.admin_user.id, 1)
        self.assertEqual(response.status_code, 406)
        self.client.cookies.clear()

        # 测试超级管理员解封管理员
        set_cookie(self.client, self.super_user)
        response = send_ban_post(self.admin_user.id, 1)
        self.assertEqual(response.status_code, 200)

        # 测试重复解封
        response = send_ban_post(self.admin_user.id, 1)
        self.assertEqual(response.status_code, 407)

        # 测试发送其他类型的请求
        response = self.client.get("/user/banned_user")
        self.assertEqual(response.status_code, 408)
        self.client.cookies.clear()

    def test_review_user(self):
        def send_review_post(review_id: int = None):
            data = {}
            if review_id is not None:
                data["id"] = review_id
            return self.client.post("/user/review_user", data=data)

        # 测试非管理员发送信息
        response = send_review_post(self.ordinary_register_user.id)
        self.assertEqual(response.status_code, 401)

        # 测试管理员不发送信息
        set_cookie(self.client, self.admin_user)
        response = send_review_post()
        self.assertEqual(response.status_code, 400)

        # 测试管理员正确审批普通待审批的用户
        response = send_review_post(self.ordinary_register_user.id)
        self.assertEqual(response.status_code, 200)

        # 测试管理员审批申请的管理员
        response = send_review_post(self.admin_register_user.id)
        self.assertEqual(response.status_code, 402)

        # 测试管理员审批已注册的用户
        response = send_review_post(self.ordinary_user.id)
        self.assertEqual(response.status_code, 403)
        self.client.cookies.clear()

        # 测试超级管理员审批管理员
        set_cookie(self.client, self.super_user)
        response = send_review_post(self.admin_register_user.id)
        self.assertEqual(response.status_code, 200)

        # 测试发送其他类型的请求
        response = self.client.get("/user/review_user")
        self.assertEqual(response.status_code, 405)
        self.client.cookies.clear()
