from django.urls import path, include

from . import views

urlpatterns = [
    path('exhibit_add', views.exhibit_add, name='exhibit_add'),
    path('exhibit_delete', views.exhibit_delete, name='exhibit_delete'),
    path('exhibits_search', views.exhibits_search, name='exhibits_search'),
    path('exhibit_modify', views.exhibit_modify, name='exhibit_modify'),
    path('exhibit_search', views.exhibit_search, name='exhibit_search'),
]