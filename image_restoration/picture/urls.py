from django.urls import path
from . import views

urlpatterns = [
    path('pictures_upload', views.pictures_upload, name='pictures_upload'),
    path('pictures_search', views.pictures_search, name='pictures_search'),
    path('pictures_delete', views.pictures_delete, name='pictures_delete'),
    path('pictures_repair', views.pictures_repair, name='pictures_repair'),
    path('picture_search', views.picture_search, name='picture_search'),
    path('picture_modify', views.picture_modify, name='picture_modify'),
    path('repairstep_delete', views.repair_step_delete, name='repair_step_delete'),
    path("init", views.init, name="pictures_init"),
]
