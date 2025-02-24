from django.urls import path
from .views import newspage, news_list, create_news

urlpatterns = [
    path('', newspage, name='newspage'),
    path('list/', news_list, name='news_list'),
    path('panel/', news_list, name='news_panel'),
    path('create/', create_news, name='create_news'),
]
