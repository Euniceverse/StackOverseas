from django.urls import path
from .views import societiespage, create_society
 
urlpatterns = [
    path('', societiespage, name='societiespage'),
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
]