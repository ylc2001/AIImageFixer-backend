import json
from django.template.defaultfilters import length
from django.test import TestCase
from tests.utils import *


class MessageModelTests(TestCase):
    # 初始化 新建管理员
    # 初始化 新建管理员
    def setUp(self):
        add_user_data(self)
        add_picture_and_exhibit_data(self)

    # 测试展览添加接口
    def test_exhibit_add(self):
        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        self.assertEqual(self.client.post('/exhibits/exhibit_add', {'title': 'test'}).status_code, 200)
        # self.assertEqual(length(Exhibit.objects.filter(id=self.secret_exhibit.id).first().tags.all()), 0)

        # 测试管理员发送错误请求 参数不全
        self.assertEqual(self.client.post('/exhibits/exhibit_add').status_code, 400)
        # self.assertEqual(length(Exhibit.objects.filter(id=self.secret_exhibit.id).first().tags.all()), 0)

        # 测试管理员发送错误请求 method error
        self.assertEqual(self.client.get('/exhibits/exhibit_add').status_code, 402)
        # self.assertEqual(length(Exhibit.objects.filter(id=self.secret_exhibit.id).first().tags.all()), 0)
        self.client.cookies.clear()

    # 测试展览删除接口
    def test_exhibit_delete(self):
        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        self.client.post("/exhibits/exhibit_delete", {'id': self.secret_exhibit.id})
        self.assertEqual(length(Exhibit.objects.filter(id=self.secret_exhibit.id)), 0)
        self.client.cookies.clear()

        # 测试管理员发送错误请求 post error
        set_cookie(self.client, self.admin_user)
        response = self.client.post("/exhibits/exhibit_delete")
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试管理员发送错误请求 method error
        set_cookie(self.client, self.admin_user)
        response = self.client.get("/exhibits/exhibit_delete")
        self.assertEqual(response.status_code, 402)
        self.client.cookies.clear()

    # 测试单个展览搜索接口
    def test_exhibit_search(self):
        def send_search_get(search_public: int = 1):
            return self.client.get("/exhibits/exhibits_search",
                                   {"public": search_public,
                                    "title": "public",
                                    "tags": ["1", "2", "3"],
                                    "time[]": [2000000000, 4000000000],
                                    'order': 0,
                                    'search_range': [1, 10]
                                    })

        # 测试被封禁的用户发送请求
        set_cookie(self.client, self.freeze_user)
        response = send_search_get(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户请求未公开数据
        set_cookie(self.client, self.ordinary_user)
        response = send_search_get(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 401)

        # 测试普通用户请求合法数据
        response = send_search_get(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试管理员用户请求隐私数据
        set_cookie(self.client, self.admin_user)
        response = send_search_get(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员发送错误的请求
        response = self.client.post("/exhibits/exhibits_search")
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试未注册用户请求公开数据
        set_cookie(self.client, self.ordinary_register_user)
        response = send_search_get(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

    # def test_exhibit_modify(self):
    #     def send_search_get(modify_id:int=None,):
    #
