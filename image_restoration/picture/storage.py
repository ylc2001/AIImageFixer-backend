from image_restoration import settings
from django.core.files.storage import FileSystemStorage


class ImageStorage(FileSystemStorage):
    def _open(self, name, mode='rb'):
        # 打开django本地文件
        pass

    # 给返回的图片标识加上前缀
    def url(self, name):
        return settings.back_url + settings.MEDIA_URL + name
