"""
URL configuration for uni_society project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import home
from apps.societies.functions import top_societies
from pathlib import Path
from .views import ai_search
from apps.events.views import event_list
BASE_DIR = Path(__file__).resolve().parent.parent  # ✅ Define BASE_DIR

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('events/', include('apps.events.urls')),
    path('news/', include('apps.news.urls')),
    path('societies/', include('apps.societies.urls')),
    path('users/', include('apps.users.urls')),
    path('search/', ai_search, name='ai_search'),
    path('api/events/', event_list, name='event_list'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=BASE_DIR / "config/static")
