from django.contrib import admin
from picture import models

admin.site.register(models.Picture)
admin.site.register(models.PictureComment)
admin.site.register(models.PictureHistory)
admin.site.register(models.RepairStep)
admin.site.register(models.Tag)
admin.site.register(models.Image)
