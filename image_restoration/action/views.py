from django.views.decorators.csrf import csrf_exempt
from exhibit.models import Exhibit, ExhibitComment
from image_restoration import settings
from image_restoration.utils import gen_response, catch_error
from picture.models import Picture, PictureComment
from user.check_login import check_identity, check_user


@csrf_exempt
def like(request):
    # 获取用户信息并校验
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user = user_dic["user"]
    if identity < 1:
        return gen_response(401, settings.message["right"])

    if request.method == "POST":
        try:
            like_type = int(request.POST['type'])
            like_id = int(request.POST["id"])
            is_like = int(request.POST["like"])
            if like_type == 1:
                like_obj = Exhibit.objects.get(id=like_id)
            elif like_type == 2:
                like_obj = Picture.objects.get(id=like_id)
            else:
                return gen_response(400, "like_type error")
            if like_obj.public == 0:
                return gen_response(400, "picture or exhibit is not public")
            if is_like == 1:
                like_obj.like_users.add(user)
                like_obj.likesNum = len(like_obj.like_users.all())
                like_obj.save()
            elif is_like == 0:
                like_obj.like_users.remove(user)
                like_obj.likesNum = len(like_obj.like_users.all())
                like_obj.save()
            else:
                return gen_response(400, settings.message["post"])
            return gen_response(200, settings.message["success"])

        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])


# 用户评论图片的接口
@csrf_exempt
def comment(request):
    # 获取用户信息,判断是否有评论权限
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user = user_dic["user"]
    if identity < 1:
        return gen_response(401, "您没有权限")

    if request.method == "POST":
        try:
            comment_type = int(request.POST["type"])
            comment_id = int(request.POST["id"])
            comment_body = request.POST["comment"]

            if comment_type == 1:
                exhibit = Exhibit.objects.get(id=comment_id)
                if exhibit.public == 0:
                    return gen_response(400, "exhibit is not public")
                if comment_body != "":
                    ExhibitComment.objects.create(user=user, body=comment_body, exhibit=exhibit)
                    return gen_response(200, settings.message["success"])
                else:
                    return gen_response(400, settings.message["post"])

            elif comment_type == 2:
                if comment_body != '':
                    picture = Picture.objects.get(id=comment_id)
                    if picture.public == 0:
                        return gen_response(400, "picture is not public")
                    PictureComment.objects.create(user=user, body=comment_body, picture=picture)
                    return gen_response(200, settings.message["success"])
                else:
                    return gen_response(400, settings.message["post"])

            else:
                return gen_response(400, settings.message["post"])

        except Exception as e:
            return gen_response(400, str(e))

    else:
        return gen_response(400, settings.message["method"])


@csrf_exempt
@catch_error
def collection(request):
    # 获取用户信息并校验
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user = user_dic["user"]
    if identity < 1:
        return gen_response(401, "您没有权限")

    if request.method == "POST":
        try:
            collection_id = int(request.POST["id"])
            collection_option = int(request.POST["option"])
            collection_type = int(request.POST["type"])
            if collection_type == 1:
                collection_obj = Exhibit.objects.get(id=collection_id)
            elif collection_type == 2:
                collection_obj = Picture.objects.get(id=collection_id)
            else:
                return gen_response(400, "type or id error")

            if collection_obj.public == 0:
                return gen_response(400, "the exhibit or picture is not public")

            if collection_option == 0:
                collection_obj.collection_users.remove(user)
            elif collection_option == 1:
                collection_obj.collection_users.add(user)
            else:
                return gen_response(400, settings.message["post"])
            collection_obj.collectionNum = len(collection_obj.collection_users.all())
            collection_obj.save()
            return gen_response(200, 'successful option')
        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])


@csrf_exempt
def delete_comment(request):
    user_dic = check_identity(request)
    identity = user_dic["identity"]
    user = user_dic["user"]
    if identity < 1:
        return gen_response(401, "you don't have right")
    if request.method == "POST":
        try:
            delete_id = int(request.POST["id"])
            delete_type = int(request.POST["type"])
            if delete_type == 1:
                delete_obj = ExhibitComment.objects.get(id=delete_id)
            elif delete_type == 2:
                delete_obj = PictureComment.objects.get(id=delete_id)
            else:
                return gen_response(400, settings.message["post"])

            if user.id == delete_obj.user.id or (abs(check_user(delete_obj.user)) < identity):
                delete_obj.delete()
                return gen_response(200, "delete successful")
            else:
                return gen_response(401, "you don't have right")
        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])
