from django.urls import path
from . import views

urlpatterns = [
    #University endpoints
    path('create/', views.create_university),
    path('get/', views.get_universities),
    path('delete/<int:university_id>', views.delete_university),
    path('edit/', views.edit_university),
    path('get/<int:university_id>/', views.get_university),
    path('edit/<int:university_id>/', views.edit_university),

    #Department endpoints
    path('createDepartment/',views.create_department)
]
