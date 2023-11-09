from django.db import models
from user.models import User
from picture.models import Picture, Tag


class Exhibit(models.Model):
    title = models.CharField(max_length=20, default="no title", verbose_name="展览标题")
    introduction = models.TextField(max_length=300, default="no introduction", verbose_name="展览介绍")
    likesNum = models.IntegerField(default=0, verbose_name="点赞数")
    style = models.IntegerField(default=0, verbose_name="样式")  # 或许用编号来代表不同的样式？
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="标签列表")
    pictures = models.ManyToManyField(to="picture.Picture", blank=True, verbose_name="图片列表")  # 多对多
    like_users = models.ManyToManyField(User, blank=True, related_name="exhibit_like",
                                        verbose_name="点过赞的用户")  # 为当前展览点过赞的用户
    collection_users = models.ManyToManyField(User, blank=True, related_name="exhibit_collection", verbose_name="收藏的用户")
    '''0:未公开 1:已公开'''
    public = models.IntegerField(default=0, verbose_name="是否公开")
    collectionNum = models.IntegerField(default=0, verbose_name="收藏数")
    time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    modify_lock = models.IntegerField(default=0, verbose_name="信息修改是否在进行")


class ExhibitComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发表的用户")
    body = models.TextField(max_length=400, verbose_name="内容")
    time = models.DateTimeField(auto_now_add=True, verbose_name="发布时间")  # 用于排序
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, verbose_name="评论的展览")


class ExhibitHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="浏览的用户")
    exhibit = models.ForeignKey(Exhibit, on_delete=models.CASCADE, verbose_name="浏览的展览")
    time = models.DateTimeField(auto_now_add=True, verbose_name="浏览时间")
