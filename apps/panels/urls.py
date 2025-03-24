from django.urls import path
from .views import *
from . import views

app_name = 'panels' 


urlpatterns = [
    path('create/', create_poll, name='create_poll'), 
    path('create_question/', views.create_poll, name='create_question'), 
    path('<int:question_id>/vote/', views.vote, name='vote'),
    path('poll/<int:question_id>/cancel_vote/', views.cancel_vote, name='cancel_vote'),
    path('poll/', views.index, name='index'),
    path('', views.panels, name='panel'),
    
]