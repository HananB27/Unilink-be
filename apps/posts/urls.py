from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_posts, name='get_posts'),
    path('create/', views.create_post, name='create_post'),
    path('update/<str:id>/', views.update_post, name='update_post'),
    path('delete/<str:uid>/', views.delete_post, name='delete_post'),
]
