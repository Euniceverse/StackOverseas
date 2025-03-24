from django.urls import path
from .views import *
from . import views

app_name = 'panels'  # This is important for the namespace


urlpatterns = [
    path('create/', create_poll, name='create_poll'),  # 질문 생성 URL
    path('create_question/', views.create_poll, name='create_question'),  # 'create_question' URL 패턴
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('poll/', views.index, name='index'),
    path('', views.panels, name='panel'),
    
]