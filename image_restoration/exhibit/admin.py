from django.contrib import admin
from exhibit import models

admin.site.register(models.Exhibit)
admin.site.register(models.ExhibitComment)
admin.site.register(models.ExhibitHistory)
