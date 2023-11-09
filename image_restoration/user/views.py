# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from image_restoration.utils import encryption, JsonResponse
from image_restoration import settings
from user.models import AvatarImage, User
from user.check_login import check_undefined, check_identity, check_user, gen_response
import os
from picture.utils import change_http_url_to_local, save_pic


# 注册请求的响应
@csrf_exempt
@check_undefined
def register(request):
    if request.method == "POST":
        try:
            # 获取前端传来的用户名和密码
            username = request.POST["username"]
            password = request.POST["password"]
            # 注册方式（管理员/用户）
            register_type = int(request.POST["identity"])
            is_admin = True if register_type == 2 else False
        except Exception as e:
            # 如果数据缺失则报错
            return gen_response(400, str(e))

        # 校验是否存在相同的用户名
        old_user = User.objects.filter(username=username)
        if old_user:
            # 如果存在返回错误代码要求重新选择用户名
            return gen_response(400, "该用户名已被占用，请重新更换用户名")
        else:
            # 可以正常注册，准备存储
            new_password = encryption(password)
            try:
                User.objects.create(username=username, password=new_password, is_admin=is_admin,
                                    img=AvatarImage.objects.create())
            except Exception as e:
                # 处理突发情况，防止在多进程多线程工作时同时创建了相同用户名的用户报错直接暴漏给前端
                return gen_response(400, str(e))
            # 注册成功，返回status_code=200
            return gen_response(200, "注册成功，等待管理员审核")
    else:
        # 该接口不接受其他请求
        return gen_response(400, settings.message["method"])


# 登录请求
# 接受post请求,登陆成功后配置id
# 接受get请求,用与判断当前用户是否为游客,能否登录
# ToDo: 加上勾选是否记住登录状态的复选框,加上后存储cookie,否则只存储session
@csrf_exempt
@check_undefined
def login(request):
    if request.method == "GET":
        # 正常来说登陆请求的用户应该是游客状态即identity=0
        return gen_response(200, "即将登录", 0)
    elif request.method == "POST":
        # 提取并检查表单中的信息
        try:
            username = request.POST['username']
            password = request.POST['password']
            # ToDo 添加记住用户选项
            is_cookie = True if (int(request.POST["remember"]) == 1) else False
        except Exception as e:
            # 提交的表单中缺少数据
            return gen_response(400, str(e), 0)

        # 尝试从数据库中找出登录的账户
        try:
            user = User.objects.get(username=username)
        # 没有在数据库中找到该用户
        except Exception as e:
            return gen_response(402, str(e), 0)

        # 校对密码
        secret_password = encryption(password)
        if secret_password != user.password:
            # 密码不匹配
            return gen_response(403, "用户名或者密码错误", 0)

        # 密码匹配,验证用户身份
        identity = check_user(user)

        # 未审批用户
        if identity == 0:
            return gen_response(405, "您尚未通过审批,请耐心等待管理员审核", identity)

        # 被封禁的用户
        elif identity < 0:
            if user.freeze:
                return gen_response(406, "您被永久封禁,尚未解除", identity)
            else:
                return_string = str(user.free_date.year) + "年" + \
                                str(user.free_date.month) + "月" + \
                                str(user.free_date.day) + "日" + \
                                str(user.free_date.hour) + "时" + \
                                str(user.free_date.minute) + "分" + \
                                str(user.free_date.second) + "秒"
                return gen_response(407, "您被封禁至" + return_string, identity)

        # 通过检验的用户,需要记住会话状态,并根据用户是否选择持久化存储来决定是否使用cookie
        else:
            request.session['username'] = username
            request.session['id'] = user.id
            request.session["identity"] = identity
            # 判断用户在是否点选了记住用户,点选后默认三天内无需登录（只要cookie还在）
            if is_cookie:
                request.session.set_expiry(3600 * 24 * 3)
                resp = gen_response(200, {"username": username, "identity": identity, 'avatar': user.avatar.url},
                                    identity)
                resp.set_cookie('username', username, 3600 * 24 * 3)
                resp.set_cookie('id', user.id, 3600 * 24 * 3)
                resp.set_cookie('identity', identity, 3600 * 24 * 3)
                return resp
            return gen_response(200, {"username": username, "identity": identity, 'avatar': user.avatar.url}, identity)
    else:
        return gen_response(408, "无法处理该类型的请求", 0)


# 退出登陆状态（注销）
@csrf_exempt
def log_out(request):
    if request.method == "POST":
        identity = check_identity(request)["identity"]
        if identity == 0:
            resp = gen_response(400, "您尚未登录！", identity)
        else:
            resp = gen_response(200, "退出成功！", identity)

        request.session.flush()

        resp.delete_cookie('username')
        resp.delete_cookie('id')
        resp.delete_cookie("identity")

        return resp
    else:
        return gen_response(400, settings.message["method"])


def delete_avatar(url: str):
    if settings.default_avatar_name not in url:
        os.remove(change_http_url_to_local(url))


def init_avatar():
    try:
        return_data = ""
        users = User.objects.all()
        for user in users:
            if settings.default_avatar_url == user.avatar.url:
                path = change_http_url_to_local(user.avatar.url)
                response = save_pic(path, user)
                return_data += response
        if return_data == "":
            return JsonResponse({"code": 200, "data": "avatar add to mysql successfully"})
        else:
            return JsonResponse({"code": 400, "data": "avatar add to mysql error: " + return_data})
    except Exception as e:
        return JsonResponse({"code": 400, "data": "avatar add to mysql error: " + str(e)}, status=400)


@csrf_exempt
def avatar_upload(request):
    user_info_dic = check_identity(request)
    identity = user_info_dic["identity"]
    user: User = user_info_dic["user"]
    if identity <= 0:
        return gen_response(401, "您未登录或被封禁，请重新登录", identity)
    if request.method == 'POST':
        try:
            avatar_file = request.FILES['file']
        except Exception as e:
            return gen_response(400, str(e))
        # 删除原有的图像
        old_url = change_http_url_to_local(user.avatar.url)
        user.avatar = avatar_file
        if user.img is None:
            user.img = AvatarImage.objects.create(img=avatar_file.read())
        else:
            user.img.img = avatar_file.read()
        user.img.save()
        user.save()
        delete_avatar(url=old_url)
        return gen_response(200, "success")

    else:
        return gen_response(400, settings.message["method"])


@csrf_exempt
def get_avatar(request):
    user_info_dic = check_identity(request)
    identity = user_info_dic["identity"]
    user: User = user_info_dic["user"]
    if identity <= 0:
        return gen_response(401, "您未登录或被封禁，请重新登录", identity)
    if request.method == 'GET':
        return gen_response(200, user.avatar.url)
    else:
        return gen_response(400, settings.message["method"])


@csrf_exempt
def init(request):
    return init_avatar()
