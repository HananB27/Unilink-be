from django.urls import path
from . import views

urlpatterns = [
    #University endpoints
    path('create/', views.createUniversity),
    path('get/', views.getUniversities),
    path('delete/<int:university_id>', views.deleteUniversity),
    path('edit/', views.editUniversity),
    path('get/<int:university_id>/', views.getUniversity),
    path('edit/<int:university_id>/', views.editUniversity),

    #Department endpoints
    path('createDepartment/',views.createDepartment)
]
