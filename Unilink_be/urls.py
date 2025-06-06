"""
URL configuration for Unilink_be project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('apps.users.urls')),
    path('api/posts/', include('apps.posts.urls')),
    path('api/relationships/', include('apps.relationships.urls')),
    path('api/universities/', include('apps.universities.urls')),
    path('api/core/', include('apps.core.urls')),
    path('api/caching/', include('apps.caching.urls')),

    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/chatbot/', include('apps.chat.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
