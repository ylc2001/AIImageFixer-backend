# -*- coding = utf-8 -*-
# @Time : 2022/3/23 21:35
# @Author : 王栋
# @File : views.py
# Software : PyCharm
from django.views.decorators.csrf import csrf_exempt
from picture.models import RepairStep, Picture
from exhibit.models import Exhibit
from picture.utils import get_pic_url, change_http_url_to_local
from user.check_login import check_unfreeze
from user.models import User
from image_restoration.utils import gen_response, encryption, catch_error
from image_restoration import settings


# 要求用户不能被封禁
# 默认根据点赞金雄排序
@csrf_exempt
@catch_error
@check_unfreeze
def index(request):
    if request.method == "GET":
        try:
            pic_num = int(request.GET.get("picNum")) if request.GET.get("picNum") else 10
            exhibit_num = int(request.GET.get("exhibitNum")) if request.GET.get("exhibitNum") else 10
        except Exception as e:
            return gen_response(400, str(e))
        # 获取点赞靠前的展览和图片的数据
        # 展览：0:未公开  1:已公开  2:全部
        # 图片：0:未修复  1:修复中  2:已修复
        exhibits = Exhibit.objects.filter(public=1).order_by("-likesNum")[:exhibit_num]
        pictures = Picture.objects.filter(public=1).order_by("-likesNum")[:pic_num]

        exhibits_data = [
            {
                "id": exhibit.id,
                "title": exhibit.title,
                "intro": exhibit.introduction,
                "style": exhibit.style,
                "time": exhibit.time.timestamp(),
                "likesNum": exhibit.likesNum,
                "tags": [tag.name for tag in exhibit.tags.all()],
                "pic": get_pic_url(
                    exhibit.pictures.first()) if exhibit.pictures.first() else settings.default_exhibit_url,
            } for exhibit in exhibits
        ]
        pictures_data = [
            {
                "id": picture.id,
                "title": picture.title,
                "intro": picture.introduction,
                'tags': [tag.name for tag in picture.tags.all()],
                "likesNum": picture.likesNum,
                "pic": get_pic_url(picture),
                "time": picture.time.timestamp(),
            } for picture in pictures
        ]
        return gen_response(200, {"exhibits": exhibits_data, "pics": pictures_data})
    else:
        return gen_response(400, "method error")


@csrf_exempt
@catch_error
def sava_pic_to_mysql(request):
    from user.views import init_avatar
    from picture.views import init_picture
    response1 = init_avatar()
    response2 = init_picture()
    code = response1.status_code + response2.status_code - 200
    data = eval(response1.content)["data"] + "; " + eval(response2.content)["data"]
    return gen_response(code, data)


@csrf_exempt
@catch_error
def init(request):
    def load_img(img_path, obj):
        try:
            with open(img_path, "wb") as file:
                file.write(obj.img.img)
            return ""
        except Exception as exp:
            return str(exp) + "; "

    message = ""
    pictures = Picture.objects.all()
    repair_steps = RepairStep.objects.all()
    users = User.objects.all()

    for picture in pictures:
        if picture.pic.url == settings.default_picture_url:
            continue
        path = change_http_url_to_local(picture.pic.url)
        message += load_img(path, picture)

    for repair in repair_steps:
        if repair.pic.url == settings.default_repair_url:
            continue
        path = change_http_url_to_local(repair.pic.url)
        message += load_img(path, repair)

    for user in users:
        if settings.default_avatar_url == user.avatar.url:
            continue
        path = change_http_url_to_local(user.avatar.url)
        message += load_img(path, user)
    if message == "":
        return gen_response(200, "all pictures init successfully")
    else:
        return gen_response(400, message)


@csrf_exempt
@catch_error
def init_user(request):
    User.objects.create(username='admin', password=encryption("123456"), is_admin=True,
                        is_register=False)
    User.objects.create(username='other_admin', password=encryption("123456"), is_admin=True,
                        is_register=False)
    User.objects.create(username="ordinary", password=encryption("123456"), is_register=False)
    User.objects.create(username="super", password=encryption("123456"), is_superuser=True,
                        is_register=False)
    User.objects.create(username="freeze", password=encryption("123456"), is_active=False,
                        freeze=True, is_register=False)
    User.objects.create(username="ordinary_register", password=encryption("123456"))
    User.objects.create(username="admin_register", password=encryption("123456"),
                        is_admin=True)
    return gen_response(200, "success")
