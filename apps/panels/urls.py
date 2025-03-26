from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *
from . import views

app_name = 'panels' 


urlpatterns = [
    path('', views.panels, name='panel'),

    path('society/<int:society_id>/poll/create/', views.create_poll, name='create_poll'),
    path('society/<int:society_id>/polls/', views.poll_list, name='poll_list'),
    path('society/<int:society_id>/poll/<int:poll_id>/question/add/', views.add_question, name='add_question'),
    path('society/<int:society_id>/poll/<int:poll_id>/question/<int:question_id>/vote/', views.vote, name='vote'),
    path('society/<int:society_id>/poll/<int:poll_id>/question/<int:question_id>/result/', views.poll_result, name='poll_result'),
    path(
    'society/<int:society_id>/poll/<int:poll_id>/question/<int:question_id>/cancel/',
    views.cancel_vote,
    name='cancel_vote'
    ),
    
    path('society/<int:society_id>/galleries/', views.society_gallery_list, name='society_gallery_list'),
    path('society/<int:society_id>/gallery/create/', views.create_gallery, name='create_gallery'),
    path('society/<int:society_id>/gallery/<int:gallery_id>/', views.gallery_detail, name='gallery_detail'),
    path('society/<int:society_id>/gallery/<int:gallery_id>/upload/', views.upload_image, name='upload_image'),
    path('society/<int:society_id>/image/<int:image_id>/delete/', views.delete_image, name='delete_image'),

    path('society/<int:society_id>/comments/', views.society_comment_feed, name='society_comment_feed'),
    path('comment/<int:society_id>/comments/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:society_id>/comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:society_id>/comments/<int:comment_id>/like/', views.toggle_like_comment, name='like_comment'),
] 
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)