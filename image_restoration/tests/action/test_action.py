# -*- coding = utf-8 -*-
# @Time : 2022/4/20 1:25
# @Author : 王栋
# @File : test_views.py
# Software : PyCharm
import json
from django.test import TestCase
from tests.utils import add_user_data, add_picture_and_exhibit_data, set_cookie
from picture.models import Picture, PictureComment
from exhibit.models import Exhibit


class Action_Test(TestCase):
    # 初始化 新建用户
    def setUp(self):
        add_user_data(self)
        add_picture_and_exhibit_data(self)

    def test_action_like_and_collection(self):
        # action_type: 0->点赞接口 1->收藏接口
        def test_like_and_collection(action_type):
            def send_post(obj_type: int, obj_id: int, option: int):
                if action_type == 0:
                    return self.client.post("/action/like",
                                            {"type": obj_type, "id": obj_id, "like": option})
                elif action_type == 1:
                    return self.client.post("/action/collection",
                                            {"type": obj_type, "id": obj_id, "option": option})

            # 测试被封禁的用户发送请求
            set_cookie(self.client, self.freeze_user)
            response = send_post(1, self.public_exhibit.id, 1)
            self.assertEqual(response.status_code, 401)
            self.client.cookies.clear()

            # 测试普通用户对公开的照片点赞
            set_cookie(self.client, self.ordinary_user)
            response = send_post(2, self.public_picture.id, 1)
            print(json.loads(response.content.decode("UTF-8"))['data'])
            print(self.public_picture.likesNum, self.public_picture.like_users.all())
            self.assertEqual(response.status_code, 200)

            # 测试普通用户取消点赞照片
            response = send_post(2, self.public_picture.id, 0)
            print(self.public_picture.likesNum, self.public_picture.like_users.all())
            self.assertEqual(response.status_code, 200)

            # 测试普通用户点赞展览
            response = send_post(1, self.public_exhibit.id, 1)
            print(json.loads(response.content.decode("UTF-8"))['data'])
            print(self.public_exhibit.likesNum, self.public_exhibit.like_users.all())
            self.assertEqual(response.status_code, 200)

            # 测试普通用户取消点赞展览
            response = send_post(1, self.public_exhibit.id, 0)
            print(json.loads(response.content.decode("UTF-8"))['data'])
            print(self.public_exhibit.likesNum, self.public_exhibit.like_users.all())
            self.assertEqual(response.status_code, 200)

            # 测试普通用户点赞私密图片
            response = send_post(2, self.secret_picture.id, 1)
            print(json.loads(response.content.decode("UTF-8"))['data'])
            print(self.secret_picture.likesNum, self.secret_picture.like_users.all())
            self.assertEqual(response.status_code, 400)

            # 测试普通用户点赞私密展览
            response = send_post(1, self.secret_exhibit.id, 1)
            print(json.loads(response.content.decode("UTF-8"))['data'])
            print(self.secret_exhibit.likesNum, self.secret_exhibit.like_users.all())
            self.assertEqual(response.status_code, 400)

            self.client.cookies.clear()

        test_like_and_collection(0)
        test_like_and_collection(1)

    def test_action_comment(self):
        def send_comment(comment_type: int, obj, comment_body: str):
            return self.client.post("/action/comment",
                                    {"type": comment_type, "id": obj.id, "comment": comment_body})

        def delete_comment(comment_type: int, obj):
            return self.client.post("/action/delete_comment",
                                    {"type": comment_type, "id": obj.id})

        def print_comment(obj=None):
            if isinstance(obj, Picture):
                comments = obj.picturecomment_set.all()
            elif isinstance(obj, Exhibit):
                comments = obj.exhibitcomment_set.all()
            else:
                comments = []
            print([{'comment': comment.body, "user": comment.user} for comment in comments])
            print(json.loads(response.content.decode("UTF-8"))['data'])

        set_cookie(self.client, self.ordinary_user)

        # 普通用户评论公开展览
        response = send_comment(1, self.public_exhibit, "public")
        self.assertEqual(response.status_code, 200)

        # 普通用户评论公开图片
        response = send_comment(2, self.public_picture, "public")
        self.assertEqual(response.status_code, 200)

        # 普通用户删除评论
        comment = PictureComment.objects.filter(user=self.ordinary_user, picture=self.public_picture).first()
        response = delete_comment(2, comment)
        self.assertEqual(response.status_code, 200)

        # 普通用户评论私密展览
        response = send_comment(1, self.secret_exhibit, "secret")
        self.assertEqual(response.status_code, 400)

        # 普通用户评论私密的图片
        response = send_comment(2, self.secret_picture, "secret")
        print_comment(self.secret_picture)
        self.assertEqual(response.status_code, 400)

        # 冻结的用户试图评论
        self.client.cookies.clear()
        set_cookie(self.client, self.freeze_user)
        response = send_comment(1, self.public_exhibit, "from freeze")
        print_comment(self.public_exhibit)
        self.assertEqual(response.status_code, 401)
