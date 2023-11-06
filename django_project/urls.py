"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
# from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # api
    path('api/v1/', include('apps.core.api_urls', namespace='v1')),
    path('api/v2/', include('apps.core.api_urls_v2', namespace='v2')),
    # local Apps
    # path("accounts/", include("apps.accounts.urls")),
    # path("__reload__/", include("django_browser_reload.urls")),  # dev
    path("accounts/", include("django.contrib.auth.urls")),
    path('', include('apps.pages.urls', namespace='pages')),
    path('reserva/', include('apps.booking.urls', namespace='booking')),
]
