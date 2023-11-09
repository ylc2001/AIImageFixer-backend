from django.template.defaultfilters import length
from django.test import TransactionTestCase
import time
from image_restoration import settings
from tests.utils import add_user_data, add_picture_and_exhibit_data, set_cookie
from picture.models import Picture


class MessageModelTests(TransactionTestCase):
    # 初始化 新建管理员
    def setUp(self):
        add_user_data(self)
        add_picture_and_exhibit_data(self)

    # 测试单个图片上传接口

    def test_pictures_upload_one(self):
        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        with open('./media/' + settings.default_picture_name, 'rb') as pic:
            response = self.client.post("/pictures/pictures_upload", {'file': pic})
            self.assertEqual(response.status_code, 200)

        # 测试管理员发送缺少参数请求
        response = self.client.post("/pictures/pictures_upload")
        self.assertEqual(response.status_code, 400)

        # 测试管理员发送错误请求
        with open('./media/' + settings.default_picture_name, 'rb') as pic:
            response = self.client.get("/pictures/pictures_upload", {'file': pic})
            self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

    # 测试图片搜索功能
    def test_pictures_search(self):

        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search", data={'repair_status': 0, 'public': 1}).json()['data']
        print(response)
        self.assertEqual(response['pictures'][0]['title'], "no title")

        # 测试管理员发送错误请求
        response = self.client.post("/pictures/pictures_search", data={'repair_status': 0, 'public': 1})
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试管理员发送请求
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search",
                                   data={'repair_status': 1, 'public': 1, 'title': "no title", 'order_type': 1,
                                         'order': 1, 'tags[]': ['tags1', 'tags2'], 'search_range[]': [1, 5]})
        # print(response)
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试封禁用户发送请求
        set_cookie(self.client, self.freeze_user)
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search", data={'repair_status': 0, 'public': 1})
        # print(response)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户申请未公开图片
        set_cookie(self.client, self.ordinary_user)
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search", data={'repair_status': 0, 'public': 0})
        # print(response)
        self.assertEqual(response.status_code, 401)

        # 测试普通用户发送错误参数请求
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search", data={'repair_status': 4, 'public': 0})
        # print(response)
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试普通用户发送错误参数请求
        for pic in Picture.objects.all():
            pic.public = 1
            pic.save()
        response = self.client.get("/pictures/pictures_search",
                                   data={'repair_status': 2, 'public': 0, 'search_range[]': [1, 2, 3]})
        # print(response)
        self.assertEqual(response.status_code, 402)
        self.client.cookies.clear()

    # 测试图片删除功能
    def test_pictures_delete(self):

        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        self.client.post("/pictures/pictures_delete", {'id': self.secret_picture.id})
        self.assertEqual(length(Picture.objects.filter(id=self.secret_picture.id)), 0)

        # 测试管理员发送缺少参数请求
        response = self.client.post("/pictures/pictures_delete")
        self.assertEqual(response.status_code, 400)

        # 测试管理员发送错误请求
        response = self.client.get("/pictures/pictures_delete", {'id': self.secret_picture.id})
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

    # 测试图片修复功能
    def test_pictures_repair(self):

        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        response = self.client.post("/pictures/pictures_repair",
                                    {'id': self.secret_picture.id, 'repair_options': '1,2,3,4,6,7,8,9'})
        time.sleep(60)
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(length(self.secret_picture.repairstep_set.all()), 8)

        # 测试管理员发送参数错误请求
        response = self.client.post("/pictures/pictures_repair",
                                    {'repair_options': '8,9'})
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员发送参数错误请求
        response = self.client.post("/pictures/pictures_repair",
                                    {'repair_options': 'hhhhh'})
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)

        # 测试管理员发送错误请求 method error
        response = self.client.get("/pictures/pictures_repair",
                                   {'id': self.secret_picture.id, 'repair_options': '8,9'})
        # print(json.loads(response.content.decode("UTF-8"))['data'])
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

    # 测试单张图片搜索
    def test_picture_search(self):

        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        response = self.client.get("/pictures/picture_search", {'id': self.secret_picture.id, 'comments': 1}).json()[
            'data']
        self.assertEqual(response['title'], "no title")
        self.client.cookies.clear()

        # 测试封禁用户发送请求
        set_cookie(self.client, self.freeze_user)
        response = self.client.get("/pictures/picture_search", {'id': self.secret_picture.id, 'comments': 1})
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

        # 测试管理员发送错误请求
        set_cookie(self.client, self.admin_user)
        response = self.client.get("/pictures/picture_search", {'comments': 1})
        self.assertEqual(response.status_code, 400)

        # 测试管理员发送错误请求
        response = self.client.get("/pictures/picture_search", {'id': self.secret_picture.id, 'comments': 4})
        self.assertEqual(response.status_code, 402)

        # 测试管理员发送错误请求
        response = self.client.post("/pictures/picture_search", {'id': self.secret_picture.id, 'comments': 1})
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

        # 测试普通用户请求无权限内容
        for pic in Picture.objects.all():
            pic.public = 0
            pic.save()
        set_cookie(self.client, self.ordinary_user)
        response = self.client.get("/pictures/picture_search", {'id': self.secret_picture.id, 'comments': 1})
        self.assertEqual(response.status_code, 401)
        self.client.cookies.clear()

    # 测试单张图片修改
    def test_picture_modify(self):

        # 测试管理员发送请求
        set_cookie(self.client, self.admin_user)
        response = self.client.post("/pictures/picture_modify",
                                    {'id': self.secret_picture.id, 'public': 1, 'title': 'no title',
                                     'intro': 'no intro', 'tags[]': []})
        self.assertEqual(response.status_code, 200)
        self.client.cookies.clear()

        # 测试管理员发送错误请求 public error
        set_cookie(self.client, self.admin_user)
        response = self.client.post("/pictures/picture_modify",
                                    {'id': self.secret_picture.id, 'public': 4, 'title': 'no title',
                                     'intro': 'no intro', 'tags[]': []})
        self.assertEqual(response.status_code, 402)
        self.client.cookies.clear()

        # 测试管理员发送错误请求 post error
        set_cookie(self.client, self.admin_user)
        response = self.client.get("/pictures/picture_modify",
                                   {'id': self.secret_picture.id, 'public': 1, 'title': 'no title', 'intro': 'no intro',
                                    'tags[]': []})
        self.assertEqual(response.status_code, 400)
        self.client.cookies.clear()

    # 测试init函数
    def test_init(self):
        response = self.client.get("/pictures/init")
        self.assertEqual(response.status_code, 200)
