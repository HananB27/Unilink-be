from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]