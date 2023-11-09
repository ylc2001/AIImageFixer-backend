# -*- coding = utf-8 -*-
# @Time : 2022/4/20 1:06
# @Author : 王栋
# @File : utils.py
# Software : PyCharm
from datetime import datetime
from image_restoration.utils import encryption
from picture.models import Picture, Image, PictureComment
from exhibit.models import Exhibit, ExhibitComment
from user.models import User


def add_user_data(self):
    self.admin_user = User.objects.create(username='admin', password=encryption("123"), is_admin=True,
                                          is_register=False)
    self.ordinary_register_user = User.objects.create(username="ordinary_register", password=encryption("123"))
    self.admin_register_user = User.objects.create(username="admin_register", password=encryption("123"),
                                                   is_admin=True)
    self.ordinary_user = User.objects.create(username="ordinary", password=encryption("123"), is_register=False)
    self.super_user = User.objects.create(username="super", password=encryption("123"), is_superuser=True,
                                          is_register=False)
    self.freeze_user = User.objects.create(username="freeze", password=encryption("123"), is_active=False,
                                           freeze=True, is_register=False)
    self.free_date_user = User.objects.create(username="free_date", password=encryption("123"), is_active=False,
                                              is_register=False, free_date=datetime.fromtimestamp(4000000000))
    self.other_admin_user = User.objects.create(username='other_admin', password=encryption("123"), is_admin=True,
                                                is_register=False)


def add_picture_and_exhibit_data(self):
    self.secret_exhibit = Exhibit.objects.create(public=0, title='secret')
    self.public_exhibit = Exhibit.objects.create(public=1, title='public')
    self.secret_exhibit.like_users.add(self.admin_user)
    self.public_exhibit.like_users.add(self.ordinary_user, self.admin_user)
    self.secret_picture = Picture.objects.create(public=0, img=Image.objects.create())
    self.public_picture = Picture.objects.create(public=1, img=Image.objects.create())
    self.secret_picture.like_users.add(self.admin_user)
    self.secret_picture.likesNum += 1
    self.public_picture.like_users.add(self.ordinary_user, self.admin_user)
    self.public_picture.likesNum += 1
    self.public_exhibit.pictures.add(self.public_picture)
    ExhibitComment.objects.create(user=self.ordinary_user, body="hhh", exhibit=self.public_exhibit)
    ExhibitComment.objects.create(user=self.admin_user, body="hhh", exhibit=self.public_exhibit)
    PictureComment.objects.create(user=self.ordinary_user, body='www', picture=self.public_picture)
    PictureComment.objects.create(user=self.admin_user, body='www', picture=self.public_picture)
    self.secret_exhibit.collection_users.add(self.admin_user)
    self.secret_exhibit.collectionNum += 1
    self.public_exhibit.collection_users.add(self.ordinary_user, self.admin_user)
    self.public_exhibit.collectionNum += 1
    self.secret_picture.collection_users.add(self.admin_user)
    self.secret_picture.collectionNum += 1
    self.public_picture.collection_users.add(self.ordinary_user, self.admin_user)
    self.public_picture.collectionNum += 1
    self.public_exhibit.save()
    self.public_picture.save()
    self.secret_exhibit.save()
    self.secret_picture.save()


# 根据传入的用户设置发送请求时的cookie值
def set_cookie(my_client, user):
    cookies = my_client.cookies
    cookies["id"] = user.id
    cookies["username"] = user.username
