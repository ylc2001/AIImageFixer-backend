from datetime import datetime
from image_restoration import settings
from django.db import models
from picture.storage import ImageStorage


class AvatarImage(models.Model):
    img = models.BinaryField()


# Create your models here.
class User(models.Model):
    # 用户名，在数据库中必须唯一
    username = models.CharField(max_length=30, unique=True, verbose_name="用户名")

    # 密码(密码使用加密方式存储到数据库中的)
    password = models.CharField(max_length=32, verbose_name="密码")

    # 该用户的创建时间
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    # 该用户的最近一次的登录时间
    last_login = models.DateTimeField(auto_now=True, verbose_name="登录时间")

    # 用户头像，如果没有上传则使用默认头像,img字段存储二进制文件
    avatar = models.ImageField(upload_to="user", default=settings.default_avatar_name, storage=ImageStorage(),
                               verbose_name="用户头像")
    img = models.OneToOneField(AvatarImage, null=True, on_delete=models.CASCADE, verbose_name="图片的二进制存储")

    # 用户邮箱地址，可以为空
    email = models.EmailField(blank=True, verbose_name="用户邮箱")

    # 该用户是否为超级管理员，即是否有权限任命其他的管理员，默认为false，设想超级用户应当唯一
    is_superuser = models.BooleanField(default=False, verbose_name="root权限")

    # 该用户是否为管理员，即是否有管理员权限，默认为false
    is_admin = models.BooleanField(default=False, verbose_name="管理员权限")

    # 该用户是否为尚未注册的人,默认值为True
    is_register = models.BooleanField(default=True, verbose_name="待注册用户")

    # 该用户是否为活跃用户（即有没有被封禁）
    is_active = models.BooleanField(default=True, verbose_name="用户是否活跃")

    # 永久封禁
    freeze = models.BooleanField(default=False, verbose_name="是否永久封禁")

    # 解封日期（如果上面的的is_active字段是true则该字段应为过去的一个时间），freeze的优先级比free_date高
    free_date = models.DateTimeField(blank=True, default=datetime.fromtimestamp(1000000000), verbose_name="解封日期")

    def __str__(self):
        return 'username: %s' % self.username
