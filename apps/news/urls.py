from django.urls import path
from .views import (
    newspage, 
    news_list, 
    create_news, 
    edit_news, 
    news_detail,
    delete_news,
    create_news_for_society
)

urlpatterns = [
    path('', newspage, name='newspage'),
    path('list/', news_list, name='news_list'),
    path('panel/', news_list, name='news_panel'),
    path('create/', create_news, name='create_news'),
    path('edit/<int:news_id>/', edit_news, name='edit_news'),
    path('view/<int:news_id>/', news_detail, name='news_detail'),
    path('delete/<int:news_id>/', delete_news, name='delete_news'),
    path('create/<int:society_id>/', create_news_for_society, name='create_news_for_society'),
]
