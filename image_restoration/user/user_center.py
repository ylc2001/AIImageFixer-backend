from django.views.decorators.csrf import csrf_exempt
from exhibit.models import ExhibitHistory, ExhibitComment
from image_restoration.utils import gen_response, catch_error
from picture.models import PictureHistory, PictureComment
from picture.utils import get_pic_url
from user.check_login import check_identity
from image_restoration import settings
from user.models import User


# action_type : 0->点赞  1->收藏 2->历史记录
def get_user_info(request, action_type):
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user: User = user_dic["user"]
    if identity < 1:
        return gen_response(401, "您没有权限", identity)

    if request.method == "GET":
        try:
            search_type = int(request.GET['type'])
            history_list = []
            # 展览类
            if search_type == 1:
                if action_type == 0:
                    filter_objs = user.exhibit_like.all()
                elif action_type == 1:
                    filter_objs = user.exhibit_collection.all()
                else:
                    history_list = ExhibitHistory.objects.filter(user=user)
                    filter_objs = [history.exhibit for history in history_list]
            # 图片类
            elif search_type == 2:
                if action_type == 0:
                    filter_objs = user.picture_like.all()
                elif action_type == 1:
                    filter_objs = user.picture_collection.all()
                else:
                    history_list = PictureHistory.objects.filter(user=user)
                    filter_objs = [history.picture for history in history_list]
            else:
                return gen_response(400, "no this type")

            response = []
            for i in range(len(filter_objs)):
                obj = filter_objs[i]
                dic = {
                    "id": obj.id,
                    'title': obj.title,
                    'intro': obj.introduction,
                    "time": obj.time.timestamp(),
                    'tags': [tag.name for tag in obj.tags.all()],
                    'likesNum': obj.likesNum,
                }
                if search_type == 1:
                    pic = get_pic_url(
                        obj.pictures.first()) if obj.pictures.all().first() else settings.default_exhibit_url
                    dic["like"] = 1 if user.exhibit_like.filter(id=obj.id) else 0
                    dic["pic"] = pic
                    dic["style"] = obj.style
                else:
                    pic = get_pic_url(obj)
                    dic["like"] = 1 if user.picture_like.filter(id=obj.id) else 0
                    dic["pic"] = pic
                if action_type == 2 and history_list:
                    dic["history_time"] = history_list[i].time.timestamp()
                response.append(dic)
            search_numbers = len(filter_objs)
            if search_type == 1:
                return gen_response(200, {"exhibits": response, "numbers": search_numbers})
            else:
                return gen_response(200, {"pictures": response, "numbers": search_numbers})

        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, "method error")


# 查找用户所有点赞的展览/图片
@csrf_exempt
@catch_error
def user_likes(request):
    return get_user_info(request, 0)


# 查找用户所有评论的展览/图片
def user_comment(request):
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user = user_dic["user"]
    if identity < 1:
        return gen_response(401, "您没有权限", identity)

    if request.method == "GET":
        try:
            like_type = int(request.GET['type'])
            # 展览类
            if like_type == 1:
                filter_comments = ExhibitComment.objects.filter(user=user)
                response = []
                for comments in filter_comments:
                    exhibit = comments.exhibit
                    response.append({
                        "id": exhibit.id,
                        'title': exhibit.title,
                        'body': comments.body,
                        'time': comments.time.timestamp(),
                    })
                search_numbers = len(response)
                return gen_response(200, {"exhibits": response, "numbers": search_numbers})
            # 图片类
            elif like_type == 2:
                filter_comments = PictureComment.objects.filter(user=user)
                response = []
                for comments in filter_comments:
                    picture = comments.picture
                    response.append({
                        "id": picture.id,
                        'title': picture.title,
                        'body': comments.body,
                        'time': comments.time.timestamp(),
                    })
                search_numbers = len(response)
                return gen_response(200, {"pictures": response, "numbers": search_numbers})
            else:
                return gen_response(400, settings.message["get"])

        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])


# 查找用户所有评论的展览/图片
@csrf_exempt
@catch_error
def user_collection(request):
    return get_user_info(request, 1)


# 查找用户的历史记录
@csrf_exempt
@catch_error
def user_history(request):
    return get_user_info(request, 2)
