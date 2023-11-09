"""image_restoration URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views import static
from image_restoration import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pictures/', include('picture.urls')),
    path('exhibits/', include('exhibit.urls')),
    path('user/', include("user.urls")),
    path('action/', include("action.urls")),
    path("init", views.init),
    path('index', views.index),
    path("add_to_mysql", views.sava_pic_to_mysql, name="add_to_mysql"),
    path("init_user", views.init_user),
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^media/(?P<path>.*)$', static.serve,
        {'document_root': settings.MEDIA_ROOT}, name='media'),
]
