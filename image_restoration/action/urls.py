from django.urls import path, include

from action import views

urlpatterns = [
    path('like', views.like, name='like'),
    path('comment', views.comment, name="comment"),
    path('collection', views.collection, name="collection"),
    path('delete_comment', views.delete_comment, name="delete_comment")
]
