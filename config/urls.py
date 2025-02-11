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
from .views import homepage
from apps.users.views import home, activate
from apps.users import views
from apps.societies.views import top_societies
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', top_societies, name='homepage'),
    path('', home, name='home'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path("activate/<uidb64>/<token>/", activate, name="activate"),
    path('events/', include('apps.events.urls')),
    path('news/', include('apps.news.urls')),
    path('societies/', include('apps.societies.urls')),
    path('users/', include('apps.users.urls')),

]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)