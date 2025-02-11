from django.urls import path
from .views import newspage, news_list, create_news
 
urlpatterns = [
    path('', newspage, name='newspage'),
    path('news/', news_list, name='news_list'),
    path('news-panel/', news_list, name='news_list'),
    path('create-news/', create_news, name='create_news'),
]
