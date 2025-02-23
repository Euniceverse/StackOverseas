from django.urls import path
# from .views import societiespage, create_society, top_societies, admin_pending_societies, admin_confirm_society_decision, my_societies
from .views import *


urlpatterns = [
    path('societiespage/', societiespage, name='societiespage'),
    path('my_societies/', my_societies, name='my_societies'),
    path('manage_societies/', view_manage_societies, name= 'manage_societies'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
    path('societies/society/<int:society_id>/admin-delete/', admin_confirm_delete, name='admin_confirm_delete'),
]