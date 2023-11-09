# -*- coding = utf-8 -*-
# @Time : 2022/4/23 15:05
# @Author : 王栋
# @File : public.py
# Software : PyCharm
from picture.models import PictureHistory
from user.check_login import check_identity
from image_restoration.utils import gen_response, change_to_float_list, get_datetime, change_to_int_list, lock, unlock
from exhibit.models import Exhibit, ExhibitHistory
from user.models import User
from picture.models import Picture, Tag
from picture.utils import test_tags, get_pic_url
from exhibit.utils import get_style_list, save_style_list


# obj_type: 1->exhibits   2->pictures
def search_objs(request, obj_type):
    # 获取用户身份
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user: User = user_dic["user"]
    # 判断用户是否被封禁
    if identity < 0:
        return gen_response(401, "您被封禁", identity)

    # 没有封禁则允许使用get方法访问
    if request.method == 'GET':
        filter_dic = {}
        try:
            # 共有项的读取
            search_public = int(request.GET['public'])
            # 获取其他非必填的字段
            search_title = request.GET.get('title')
            search_tags = request.GET.getlist('tags[]')
            search_timestamp = change_to_float_list(request.GET.getlist('time[]'))
            search_time = [get_datetime(i) for i in search_timestamp]
            order = int(request.GET.get("order")) if request.GET.get("order") else None
            order_type = int(request.GET.get("order_type")) if request.GET.get("order_type") else None
            search_range = change_to_int_list(request.GET.getlist('search_range[]'))
            if (search_range and len(search_range) != 2) or (search_time and len(search_time) != 2):
                return gen_response(402, "list error")

            # 普通用户只能访问公开的图片
            if identity <= 1 and search_public != 1:
                return gen_response(401, "您没有权限访问该数据", identity)

            # 获取搜索的公开属性
            if search_public != 2:
                filter_dic["public"] = search_public
            if search_title:
                filter_dic['title__contains'] = search_title
            if search_time:
                filter_dic['time__in'] = search_time
        except Exception as e:
            return gen_response(400, 'get error:' + str(e), identity)

        # 对图片的特殊处理
        if obj_type == 2:
            # pictures_Search中的特有的字段读取
            try:
                exhibit_id = int(request.GET.get("exhibit_id")) if request.GET.get("exhibit_id") else None
                search_status = int(request.GET["repair_status"])
                if search_status > 2 or search_status < 0:
                    return gen_response(405, "repair status error")

                # 通过字典进行图片筛选
                if exhibit_id is not None:
                    try:
                        exhibit = Exhibit.objects.get(id=exhibit_id)
                        if identity == 0 and exhibit.public == 0:
                            return gen_response(401, "right error")
                        filter_objs = Exhibit.objects.get(id=exhibit_id).pictures.all()
                    except Exception as e:
                        return gen_response(402, str(e))
                else:
                    filter_objs = Picture.objects.all()
                # 获取搜索的修复状态
                if search_status == 0:
                    filter_dic["repair_times"] = 0
                elif search_status == 1:
                    filter_dic["repair_times__gt"] = 0
            except Exception as e:
                return gen_response(400, 'get error:' + str(e), identity)
        else:
            filter_objs = Exhibit.objects.all()

        filter_objs = filter_objs.filter(**filter_dic)

        # 排序
        if order_type == 0:
            filter_objs = filter_objs.order_by('-likesNum')
        elif order_type == 1 or order_type is None:
            filter_objs = filter_objs.order_by('-time')
        else:
            return gen_response(406, "post error")

        if order == 0:
            filter_objs = filter_objs.reverse()
        elif order is not None and order != 1:
            return gen_response(407, "post error")

        # 根据标签筛选
        if search_tags:
            objs = []
            for obj in filter_objs:
                if test_tags(obj, search_tags):
                    objs.append(obj)
            filter_objs = objs

        # 查询完成，得到查询的结果总数
        search_numbers = len(filter_objs)

        # 从查询结果中取出特定区间内的picture
        if search_range:
            filter_objs = filter_objs[search_range[0]:search_range[1]]

        # 向返回的数据中添加信息
        response = []
        for obj in filter_objs:
            data = {
                "id": obj.id,
                'title': obj.title,
                'intro': obj.introduction,
                'tags': [tag.name for tag in obj.tags.all()],
                'likesNum': obj.likesNum,
                'collectionNum': obj.collectionNum,
                'pic': get_pic_url(obj),  # 返回url
                "like": 0,
                "collection": 0,
                'time': obj.time.timestamp(),
            }
            if obj_type == 1:
                data["style"] = get_style_list(obj.style)
            response.append(data)

        # 根据用户信息确认用户是否对其点过赞
        if identity != 0:
            # 注册用户需要判断
            for i in range(len(filter_objs)):
                if filter_objs[i].like_users.filter(id=user.id).first():
                    response[i]["like"] = 1
                if filter_objs[i].collection_users.filter(id=user.id).first():
                    response[i]["collection"] = 1

        if obj_type == 1:
            return gen_response(200, {"exhibits": response, "numbers": search_numbers}, identity)
        else:
            return gen_response(200, {"pictures": response, "numbers": search_numbers}, identity)

    else:
        return gen_response(400, 'method error')


def modify_obj(request, obj_type):
    if request.method == 'POST':
        try:
            # 必填项的校验
            modify_id = int(request.POST['id'])
            # 非必填项的校验
            modify_public = int(request.POST.get("public")) if request.POST.get("public") else None
            modify_title = request.POST.get('title')
            modify_intro = request.POST.get('intro')
            modify_tags_name = request.POST.get('tags').split(",") if request.POST.get('tags') else []
            modify_tags = []
            modify_style = None
            modify_pictures = []
            for tag_name in modify_tags_name:
                if tag_name:
                    modify_tags.append(Tag.objects.get(name=tag_name))
            # 对属性合法性的校验
            if (modify_public is not None) and (modify_public > 1 or modify_public < 0):
                return gen_response(402, "public error")

            obj = Exhibit.objects.get(id=modify_id) if obj_type == 1 else Picture.objects.get(id=modify_id)
            if lock(obj) < 0:
                return gen_response(400, "object has been locked, please wait")
        except Exception as e:
            return gen_response(400, str(e))

        try:
            # 对picture的特殊处理
            if obj_type == 1:
                modify_pictures_id = change_to_int_list(request.POST.get('pictures').split(",")) if request.POST.get(
                    'pictures') else []
                for picture_id in modify_pictures_id:
                    new_picture = Picture.objects.get(id=picture_id)
                    modify_pictures.append(new_picture)
                # 返回一个int
                modify_style = save_style_list(request.POST.get('style')) if request.POST.get("style") else None
                if modify_style is not None and modify_style < 0:
                    return gen_response(400, "style error")
                if modify_pictures:
                    obj.pictures.clear()
                    for new_picture in modify_pictures:
                        # 为展览中添加的图片只能是公开的
                        obj.pictures.add(new_picture)

            if modify_title:
                obj.title = modify_title
            if modify_intro:
                obj.introduction = modify_intro
            if modify_style is not None:
                obj.style = modify_style
            # 填入展览的公开属性
            if modify_public is not None:
                obj.public = modify_public
            # 填入展览的标签
            if modify_tags:
                obj.tags.clear()
                for new_tag in modify_tags:
                    obj.tags.add(new_tag)

            unlock(obj)
            return gen_response(200, 'success')
        except Exception as e:
            unlock(obj)
            return gen_response(400, str(e))

    else:
        return gen_response(400, 'method error')


def search_obj(request, obj_type):
    # 先做用户信息校验,由于涉及到用户是否点过赞,所以不能直接使用装饰器
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user: User = user_dic["user"]
    if identity < 0:
        return gen_response(401, "您已被封禁", identity)

    if request.method == 'GET':
        # id和comments均为必填的参数,先做校验
        try:
            search_id = int(request.GET['id'])
            search_comments = int(request.GET['comments'])
            if obj_type == 1:
                obj = Exhibit.objects.get(id=search_id)
            elif obj_type == 2:
                obj = Picture.objects.get(id=search_id)
            else:
                return gen_response(404, "obj_type error")
            if search_comments != 0 and search_comments != 1:
                return gen_response(402, "comments error")
        except Exception as e:
            return gen_response(400, str(e), identity)

        # 校验图片的是否为公开的,如果不是则普通用户和游客不能访问
        if identity <= 1 and obj.public != 1:
            return gen_response(401, "您没有权限访问", identity)

        # 返回数据的填写
        response_data = {
            'id': obj.id,
            'title': obj.title,
            'intro': obj.introduction,
            'tags': [tag.name for tag in obj.tags.all()],
            'likesNum': obj.likesNum,
            'collectionNum': obj.collectionNum,
            'time': obj.time.timestamp(),
            "like": 0,
            'collection': 0,
            "public": obj.public,
        }
        # 检查用户是否点赞过，收藏过，并记录浏览历史
        if identity != 0:
            if obj.like_users.filter(id=user.id):
                response_data['like'] = 1
            if obj.collection_users.filter(id=user.id):
                response_data['collection'] = 1
        # 添加用户的评论
        if search_comments:
            comments = obj.picturecomment_set.all() if obj_type == 2 else obj.exhibitcomment_set.all()
            response_data['comments'] = [
                {"body": comment.body, "time": comment.time.timestamp(), "username": comment.user.username,
                 "comment_id": comment.id, "avatar": comment.user.avatar.url} for comment in
                comments]
        # 对图片的特殊处理
        if obj_type == 2:
            pic = [obj.pic.url]
            repair_detail = ["上传图片"]
            response_data["repair_numbers"] = obj.repair_already + 1
            response_data["repair_status"] = obj.repair_times
            # 添加修复步骤调用的api名称以及对应的图片
            for step in obj.repairstep_set.all():
                pic.append(step.pic.url)
                repair_detail.append(step.api)
            response_data["pic"] = pic
            response_data["repair_detail"] = repair_detail
            if identity != 0:
                PictureHistory.objects.filter(user=user, picture=obj).delete()
                PictureHistory.objects.create(user=user, picture=obj)
        else:
            if identity != 0:
                ExhibitHistory.objects.filter(user=user, exhibit=obj).delete()
                ExhibitHistory.objects.create(user=user, exhibit=obj)

        return gen_response(200, response_data)

    else:
        return gen_response(400, 'method error')
