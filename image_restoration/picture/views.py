import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from image_restoration.public import search_objs, modify_obj, search_obj
from user.check_login import check_admin
from picture.models import RepairStep, Picture, Image
from image_restoration.utils import catch_error, gen_response
from picture.restoration import restoration
from picture.utils import change_http_url_to_local, save_pic, MyThread, limit_decor
from image_restoration import settings


def init_picture():
    def save_pics(objs):
        return_data = ""
        for obj in objs:
            if settings.default_picture_url == obj.pic.url or settings.default_repair_url == obj.pic.url:
                continue
            path = change_http_url_to_local(obj.pic.url)
            return_data += save_pic(path, obj)
        return return_data

    pictures = Picture.objects.all()
    repair_steps = RepairStep.objects.all()
    response = save_pics(pictures) + save_pics(repair_steps)
    if response != "":
        return gen_response(400, "pic add to mysql error: " + response)
    else:
        return gen_response(200, "pic add to mysql successfully")


@csrf_exempt
@catch_error
def init(request):
    return init_picture()


# 上传图片
@csrf_exempt
@catch_error
@check_admin
def pictures_upload(request):
    if request.method == "OPTIONS":
        return gen_response(204, "success")
    elif request.method == 'POST':
        try:
            picture_file = request.FILES['file']
        except Exception as e:
            return gen_response(400, str(e))
        title = picture_file.name
        Picture.objects.create(title=title, pic=picture_file, img=Image.objects.create(img=picture_file.read()))

        return gen_response(200, "success")

    else:
        return gen_response(400, settings.message["method"])


# 未被封禁的用户查找图片接口
@csrf_exempt
@catch_error
def pictures_search(request):
    return search_objs(request, 2)


# 管理员删除图片的接口
@csrf_exempt
@check_admin
def pictures_delete(request):
    if request.method == 'POST':
        try:
            delete_id = int(request.POST['id'])
            delete_obj = Picture.objects.get(id=delete_id)
        except Exception as e:
            return gen_response(400, str(e))

        delete_obj.like_users.clear()
        delete_obj.collection_users.clear()
        delete_obj.delete()
        return gen_response(200, 'success')

    else:
        return gen_response(400, settings.message["method"])


# 多线程的修复接口
@limit_decor(30)
def restore_pic(repair_step: RepairStep, pred_step_pic_url: str, save_name: str):
    try:
        pic_data = restoration(repair_step.api, pred_step_pic_url)
        content_file = ContentFile(base64.b64decode(pic_data['image']), "image.jpeg")
        repair_step.img = Image.objects.create(img=content_file.read())
        repair_step.img.save()
        repair_step.save()
        repair_step.pic.save(save_name, content_file)
        repair_step.save()
        repair_step.picture.repair_already += 1
        repair_step.picture.save()
        return 0
    except Exception:
        return -1


def repair_run(begin, end, repair_picture: Picture):
    repair_steps = repair_picture.repairstep_set.all()
    save_name = repair_picture.pic.name.replace("pictures/", "")
    for i in range(begin, end):
        repair_step = repair_steps[i]
        if i == 0:
            pred_step_pic_url = repair_picture.pic.url
        else:
            pred_step_pic_url = repair_steps[i - 1].pic.url

        thread = MyThread(target=restore_pic, args=(repair_step, pred_step_pic_url, save_name))
        thread.start()
        thread.join()
        result = thread.get_result()
        if result == -1:
            error_message = []
            for j in range(end - 1, i - 1, -1):
                error_step = repair_steps[j]
                if error_step.pic.url == settings.default_repair_url:
                    error_message.append(error_step.api)
                    error_step.delete()
            repair_picture.repair_times = repair_picture.repairstep_set.all().count()
            repair_picture.repair_already = repair_picture.repair_times
            repair_picture.repair_lock = 0
            repair_picture.save()
            return error_message
    # 正常结束
    repair_picture.repair_lock = 0
    repair_picture.save()
    return []


# 管理员修复图片的接口
@csrf_exempt
@check_admin
def pictures_repair(request):
    if request.method == 'POST':
        try:
            repair_id = int(request.POST['id'])
            repair_options = request.POST.get('repair_options').split(',') if request.POST.get('repair_options') else []
            repair_picture = Picture.objects.get(id=repair_id)
            if repair_picture.repair_lock == 0:
                repair_picture.repair_lock = 1
                repair_picture.save()
            else:
                return gen_response(400, "the object has been locked, please wait")
        except Exception as e:
            return gen_response(400, str(e))
        # 首先根据修复操作序列，给repair_picture建立所有的修复外键
        try:
            old_repair_num = repair_picture.repairstep_set.all().count()

            for i in range(len(repair_options)):
                RepairStep.objects.create(api=repair_options[i], picture=repair_picture, step=i + old_repair_num)
            repair_picture.repair_times = repair_picture.repairstep_set.all().count()
            repair_picture.save()
            # 进行修复操作，并将结果存入数据库
            new_repair_num = repair_picture.repair_times

            error_message = repair_run(old_repair_num, new_repair_num, repair_picture)
            code = 200 if error_message == [] else 400
            return gen_response(code, error_message)
        except Exception as e:
            repair_picture.repair_lock = 0
            repair_picture.save()
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])


# 删除最后一个repair step
@csrf_exempt
@check_admin
def repair_step_delete(request):
    if request.method == 'POST':
        try:
            repair_id = int(request.POST['id'])
            repair_picture = Picture.objects.get(id=repair_id)
        except Exception as e:
            return gen_response(400, str(e))
        try:
            old_repair_num = repair_picture.repairstep_set.all().count()
            last_repair_step = RepairStep.objects.filter(picture=repair_picture, step=old_repair_num).first()
            last_repair_step.delete()
            return gen_response(200, 'success')
        except Exception as e:
            return gen_response(400, str(e))
    else:
        return gen_response(400, settings.message["method"])


# 获取单张图片的所有信息(由于渲染图片修复详情页面)
@csrf_exempt
@catch_error
def picture_search(request):
    return search_obj(request, 2)


# 管理员编辑图片的信息
@csrf_exempt
@catch_error
@check_admin
def picture_modify(request):
    return modify_obj(request, 2)
