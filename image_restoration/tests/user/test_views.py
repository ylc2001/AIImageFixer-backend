import os
from django.test import TestCase
from picture.utils import change_http_url_to_local
from tests.utils import *


class TestUserViews(TestCase):
    # 初始化 新建用户
    def setUp(self):
        add_user_data(self)

    def test_register(self):
        def send_register_post(username: str = None, password: str = None, identity: int = None):
            data = {}
            if username:
                data["username"] = username
            if password:
                data["password"] = password
            if identity:
                data["identity"] = identity
            return self.client.post("/user/register", data=data, )

        # 测试一个被封禁的用户
        set_cookie(self.client, self.freeze_user)
        response = send_register_post("post_from_freeze", "123", 1)
        self.assertEqual(response.status_code, 401)

        # 测试没有传送数据
        response = send_register_post()
        self.assertEqual(response.status_code, 400)

        # 测试注册一个已经有过的用户名
        response = send_register_post("admin", "123", 1)
        self.assertEqual(response.status_code, 400)

        # 测试正常注册
        response = send_register_post("Alice", "123", 1)
        self.assertEqual(response.status_code, 200)

        # 发送除了post请求外的请求
        response = self.client.get("/user/register")
        self.assertEqual(response.status_code, 400)

    # 测试登录接口
    def test_login(self):
        def send_login_post(username: str = None, password: str = None, is_cookie: bool = False):
            data = {}
            if username:
                data["username"] = username
            if password:
                data["password"] = password
            data["remember"] = 1
            return self.client.post("/user/login", data=data)

        # 测试已登录状态尝试登录
        set_cookie(self.client, self.admin_user)
        response = send_login_post("admin", "123")
        self.assertEqual(response.status_code, 401)

        # 测试没有发送数据
        self.client.cookies.clear()
        response = send_login_post()
        self.assertEqual(response.status_code, 400)

        # 测试传入的用户不在数据库中
        response = send_login_post("Alice", "123")
        self.assertEqual(response.status_code, 402)

        # 测试传入错误的密码
        response = send_login_post("admin", "xyz")
        self.assertEqual(response.status_code, 403)

        # 测试传入未审批的用户
        response = send_login_post("ordinary_register", "123")
        self.assertEqual(response.status_code, 405)

        # 测试传入被永久封禁的用户
        response = send_login_post("freeze", "123")
        self.assertEqual(response.status_code, 406)

        # 测试传入被封禁至2099年的用户
        response = send_login_post("free_date", "123")
        self.assertEqual(response.status_code, 407)

        # 测试登录的用户记住登录状态
        response = send_login_post("ordinary", "123", True)
        print(self.client.cookies)
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试发送get请求
        response = self.client.get("/user/login")
        self.assertEqual(response.status_code, 200)

        # 测试发送delete请求
        response = self.client.delete("/user/login")
        self.assertEqual(response.status_code, 408)

    def test_log_out(self):
        # 测试未注册用户的注销
        response = self.client.post("/user/log_out")
        self.assertEqual(response.status_code, 400)

        # 测试正常用户的注销
        set_cookie(self.client, self.admin_user)
        response = self.client.post("/user/log_out")
        self.assertEqual(response.status_code, 200)

        # 测试其他类型的请求
        response = self.client.get("/user/log_out")
        self.assertEqual(response.status_code, 400)

    def test_upload_avatar(self):
        set_cookie(self.client, self.admin_user)
        with open('./media/default/for_test.png', 'rb') as pic:
            response = self.client.post("/user/avatar_upload", {'file': pic})
            self.admin_user = User.objects.get(id=self.admin_user.id)
            os.remove(change_http_url_to_local(self.admin_user.avatar.url))
            self.assertEqual(response.status_code, 200)
            self.client.cookies.clear()
            set_cookie(self.client, self.freeze_user)
            response = self.client.post("/user/avatar_upload", {'file': pic})
            self.assertEqual(response.status_code, 401)

    def test_get_avatar(self):
        set_cookie(self.client, self.admin_user)
        response = self.client.get('/user/get_avatar')
        self.assertEqual(response.status_code, 200)

    def test_init(self):
        set_cookie(self.client, self.admin_user)
        with open('./media/default/for_test.png', 'rb') as pic:
            response = self.client.post("/user/avatar_upload", {'file': pic})
            self.assertEqual(response.status_code, 200)
        self.admin_user = User.objects.get(id=self.admin_user.id)
        response = self.client.get("/user/init")
        self.assertEqual(response.status_code, 200)
        os.remove(change_http_url_to_local(self.admin_user.avatar.url))
