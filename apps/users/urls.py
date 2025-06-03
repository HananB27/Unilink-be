from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('hello/', views.hello),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete/<int:user_id>/', views.delete_user, name='delete'),
    path('add_friend/<str:target_email>/', views.add_friend, name='add_friend'),
    path('remove_friend/<str:target_email>/', views.remove_friend, name='remove_friend'),
    path('interested_in/<str:tag_name>/', views.user_interest_toggle, name='user_interest_toggle'),


    path('likes/<int:post_id>/', views.likes, name='like'),
]