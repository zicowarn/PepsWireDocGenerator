"""myapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import django
try:
    from django.conf.urls import url, include  # @UnusedImport
except:
    from django.urls import path as url
    from django.urls import include, re_path
from django.contrib import admin
from django.conf import settings  # @UnusedImport
from . import views


django_version = django.__version__

print("Django version:", django_version)

if django_version.startswith('4.2'):
    urlpatterns = [
        re_path(r'^admin/', admin.site.urls),
        re_path('', views.index),  # 使用 path() 替代 url()
        re_path(r'^\.?$', views.index),  # `使用 re_path() 替代 url()
    ]
else:
    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'$', views.index),
        url(r'\.?', views.index),
    ]
