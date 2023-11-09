# -*- coding = utf-8 -*-
# @Time : 2022/3/21 1:51
# @Author : 王栋
# @File : urls.py
# Software : PyCharm
from re import U
from django.urls import path
from user import views
from user import manage_user
from user import user_center

urlpatterns = [
    path('register', views.register),
    path('login', views.login),
    path('log_out', views.log_out),
    path('init', views.init),
    path('avatar_upload', views.avatar_upload),
    path('get_avatar', views.get_avatar),
    path('search_user', manage_user.search_user),
    path('delete_user', manage_user.delete_user),
    path('banned_user', manage_user.banned_user),
    path('review_user', manage_user.review_user),
    path('user_likes', user_center.user_likes),
    path('user_comment', user_center.user_comment),
    path('user_collection', user_center.user_collection),
    path('user_history', user_center.user_history),
]
