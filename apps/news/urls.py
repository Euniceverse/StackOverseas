from django.urls import path
from .views import newspage, news_list
 
urlpatterns = [
    path('', newspage, name='newspage'),
    path('news/', news_list, name="news_list"),
]