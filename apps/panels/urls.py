from django.conf import settings
from django.conf.urls.static import static
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
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/<int:gallery_id>/', views.gallery_detail, name='gallery_detail'),
    path('gallery/upload/', upload_gallery, name='upload_gallery'),
    path('image/delete/<int:image_id>/', views.delete_image, name='delete_image'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)