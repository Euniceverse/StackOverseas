from django.urls import path
from .views import societiespage, create_society, top_societies, admin_pending_societies, admin_confirm_society_decision

urlpatterns = [
    path('', societiespage, name='societiespage'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
]