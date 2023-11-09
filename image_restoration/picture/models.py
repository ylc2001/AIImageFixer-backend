from image_restoration import settings
from django.db import models
from user.models import User
from .storage import ImageStorage


# Create your models here.

class Image(models.Model):
    img = models.BinaryField()


# ToDo Tag必须用models吗，可以固定tag后只让用户选择，存储index吗
class Tag(models.Model):
    name = models.CharField(max_length=10, unique=True, verbose_name="标签")

    def __str__(self):
        return self.name


class Picture(models.Model):
    # 图片名称，简介，点赞数目，添加/发布的时间，标签，图片文件，图片类型
    title = models.CharField(max_length=50, default="no title", verbose_name="图片标题")
    introduction = models.TextField(max_length=300, default="no introduction", verbose_name="图片介绍")
    likesNum = models.IntegerField(default=0, verbose_name="图片的点赞")
    time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="标签列表")
    pic = models.ImageField(upload_to='pictures', storage=ImageStorage(), default=settings.default_picture_name,
                            verbose_name="图片文件")
    public = models.IntegerField(default=0, verbose_name="图片是否公开")
    like_users = models.ManyToManyField(User, blank=True, related_name="picture_like", verbose_name="点赞的用户")
    collection_users = models.ManyToManyField(User, blank=True, related_name="picture_collection", verbose_name="收藏的用户")
    collectionNum = models.IntegerField(default=0, verbose_name="收藏数")
    img = models.OneToOneField(Image, on_delete=models.CASCADE, verbose_name="图片的二进制存储")
    repair_already = models.IntegerField(default=0, verbose_name="已完成的修复步骤数")
    repair_times = models.IntegerField(default=0, verbose_name="修复操作数目")
    repair_lock = models.IntegerField(default=0, verbose_name="修复是否在进行中")
    modify_lock = models.IntegerField(default=0, verbose_name="信息修改是否在进行")

    def __str__(self):
        return self.title


class PictureComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="发表的用户")
    body = models.TextField(max_length=400, verbose_name="评论内容")
    time = models.DateTimeField(auto_now_add=True, verbose_name="发表的时间")  # 评论的发表时间
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, verbose_name="评论的图片")

    def __str__(self):
        return self.body


class RepairStep(models.Model):
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, verbose_name="修复的图片")
    step = models.IntegerField(default=0, verbose_name="修复的步骤")  # 用来排序,暂时没有使用
    api = models.CharField(max_length=50, verbose_name="调用的接口")
    pic = models.ImageField(upload_to='repair', storage=ImageStorage(), default=settings.default_repair_name,
                            verbose_name="修复后的图片")  # 上传还需要调试
    # 存储在mysql中的二进制数据，用于重启容器时恢复数据使用
    img = models.OneToOneField(Image, null=True, on_delete=models.CASCADE, verbose_name="图片的二进制存储")

    def __str__(self):
        return self.api


class PictureHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="浏览的用户")
    picture = models.ForeignKey(Picture, on_delete=models.CASCADE, verbose_name="浏览的展览")
    time = models.DateTimeField(auto_now_add=True, verbose_name="浏览时间")
