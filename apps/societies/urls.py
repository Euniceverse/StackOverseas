from django.urls import path
from .views import (societiespage,
                    create_society, 
                    top_societies, 
                    admin_pending_societies, 
                    admin_confirm_society_decision, 
                    my_societies, 
                    request_delete_society, 
                    admin_confirm_delete)


urlpatterns = [
    path('societiespage/', societiespage, name='societiespage'),
    path('my_societies/', my_societies, name='my_societies'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),

    #admin
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
    #path('admin/review-deletion-requests/', admin_review_deletion_requests, name="admin_review_deletion_requests"),
    path('admin/review-deletion-requests/', admin_confirm_delete, name="admin_confirm_delete"),
    path('admin/delete/<int:society_id>/<str:action>/', admin_confirm_delete, name="admin_confirm_delete"),

    #society delete request
    path('society/<int:society_id>/request-delete/', request_delete_society, name="request_delete_society"),
]