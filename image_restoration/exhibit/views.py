from image_restoration import settings
from image_restoration.public import search_objs, modify_obj
from image_restoration.utils import catch_error
from django.views.decorators.csrf import csrf_exempt
from exhibit.models import Exhibit
from user.check_login import check_admin, gen_response
from picture.models import Tag


# 创建展览
@csrf_exempt
@check_admin
def exhibit_add(request):
    if request.method == 'POST':
        try:
            # 标题是必须要添加的项
            add_title = request.POST['title']
            # 其他的非必填项,注意处理不传/传空的情况
            add_intro = request.POST.get('intro')
            # 默认样式是0
            add_style = int(request.POST.get('style')) if request.POST.get("style") else 0
            add_tags = request.POST.get('tags').split(",") if request.POST.get('tags') else []
            tags_list = []
            for tag in add_tags:
                if tag:
                    tags_list.append(Tag.objects.get(name=tag))
            new_exhibit = Exhibit.objects.create(title=add_title)
        except Exception as e:
            return gen_response(400, str(e))

        if add_intro:
            new_exhibit.introduction = add_intro
        # default值为0,所以只需要考虑非0的情况
        if add_style != 0:
            new_exhibit.style = add_style
        for new_tag in tags_list:
            new_exhibit.tags.add(new_tag)

        new_exhibit.save()
        return gen_response(200, 'success')

    else:
        return gen_response(402, settings.message["method"])


# 删除展览
@csrf_exempt
@check_admin
def exhibit_delete(request):
    if request.method == 'POST':
        try:
            delete_id = int(request.POST['id'])
            delete_exhibit = Exhibit.objects.filter(id=delete_id)
        except Exception as e:
            return gen_response(400, str(e))
        delete_exhibit.delete()
        return gen_response(200, 'success')

    else:
        return gen_response(402, settings.message["method"])


# 根据条件查找展览
# TODO 搜索优化
@csrf_exempt
@catch_error
def exhibits_search(request):
    return search_objs(request, 1)


# 修改展览信息
# TODO 增量式修改
@csrf_exempt
@check_admin
def exhibit_modify(request):
    return modify_obj(request, 1)


# 单个展览查询（用于渲染展览界面）
@csrf_exempt
def exhibit_search(request):
    return search_objs(request, 1)
