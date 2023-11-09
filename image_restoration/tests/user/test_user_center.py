from django.test import TestCase, client
from tests.utils import add_user_data, add_picture_and_exhibit_data, set_cookie
import json


class UserCenterTest(TestCase):
    # 初始化 新建用户
    def setUp(self):
        add_user_data(self)
        add_picture_and_exhibit_data(self)

    def test_user_likes(self):
        def send_user_likes(search_type: int = 1):
            return self.client.get("/user/user_likes",
                                   {"type": search_type})

        # 测试被封禁的用户发送请求
        set_cookie(self.client, self.freeze_user)
        response = send_user_likes(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户请求点赞照片
        set_cookie(self.client, self.ordinary_user)
        response = send_user_likes(2)
        # print(Picture.objects.all())
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试普通用户请求点赞展览
        response = send_user_likes(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试管理员用户请求点赞照片
        set_cookie(self.client, self.admin_user)
        response = send_user_likes(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户请求点赞展览
        response = send_user_likes(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户发送错误请求 type error
        response = send_user_likes(3)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 参数错误
        response = self.client.get("/user/user_likes")
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 method error
        response = self.client.post("/user/user_likes", {"type": 1})
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试未注册用户请求数据
        set_cookie(self.client, self.ordinary_register_user)
        response = send_user_likes(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

    def test_user_comments(self):
        def send_user_comment(search_type: int = 1):
            return self.client.get("/user/user_comment",
                                   {"type": search_type})

        # 测试被封禁的用户发送请求
        set_cookie(self.client, self.freeze_user)
        response = send_user_comment(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户请求评论照片
        set_cookie(self.client, self.ordinary_user)
        response = send_user_comment(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试普通用户请求评论展览
        response = send_user_comment(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试管理员用户请求评论照片
        set_cookie(self.client, self.admin_user)
        response = send_user_comment(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户请求评论展览
        response = send_user_comment(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户发送错误请求 type error
        response = send_user_comment(3)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 参数错误
        response = self.client.get("/user/user_comment")
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 method error
        response = self.client.post("/user/user_comment", {"type": 1})
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试未注册用户请求数据
        set_cookie(self.client, self.ordinary_register_user)
        response = send_user_comment(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

    def test_user_collection(self):
        def send_user_collection(search_type: int = 1):
            return self.client.get("/user/user_collection",
                                   {"type": search_type})

        # 测试被封禁的用户发送请求
        set_cookie(self.client, self.freeze_user)
        response = send_user_collection(1)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户请求收藏照片
        set_cookie(self.client, self.ordinary_user)
        response = send_user_collection(2)
        # print(Picture.objects.all())
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试普通用户请求收藏展览
        response = send_user_collection(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试管理员用户请求收藏照片
        set_cookie(self.client, self.admin_user)
        response = send_user_collection(2)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户请求收藏展览
        response = send_user_collection(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)

        # 测试管理员用户发送错误请求 type error
        response = send_user_collection(3)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 参数错误
        response = self.client.get("/user/user_collection")
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员用户发送错误请求 method error
        response = self.client.post("/user/user_collection", {"type": 1})
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试未注册用户请求数据
        set_cookie(self.client, self.ordinary_register_user)
        response = send_user_collection(1)
        print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

    # TODO 当一个展览在被访问后被设置为了私密的，那么用户在浏览历史中能否看到呢？
    def test_user_history(self):
        def send_user_history(search_type: int):
            return self.client.get("/user/user_history",
                                   {"type": search_type})

        def send_search(search_type: int, obj):
            if search_type == 1:
                return self.client.get("/exhibits/exhibit_search", {"id": obj.id, "comments": 1})
            elif search_type == 2:
                return self.client.get("/pictures/picture_search", {'id': obj.id, "comments": 1})
            else:
                return None

        set_cookie(self.client, self.admin_user)
        send_search(1, self.public_exhibit)
        send_search(2, self.public_picture)
        response = send_user_history(1)
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
        response = send_user_history(2)
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 200)
