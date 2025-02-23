from django.urls import path
from .views import (
    societiespage, 
    create_society, 
    admin_pending_societies, 
    admin_confirm_society_decision, 
    my_societies, 
    manage_society, 
    update_membership,
    society_detail,
    join_society,
    view_applications,
    decide_application,
)
from .functions import top_societies

urlpatterns = [
    path('societiespage/', societiespage, name='societiespage'),
    path('my_societies/', my_societies, name='my_societies'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
    path('<int:society_id>/manage/', manage_society, name='manage_society'),
    path('<int:society_id>/membership/<int:user_id>/update/', update_membership, name='update_membership'),
    path('<int:society_id>/', society_detail, name='society_detail'),
    path('<int:society_id>/join/', join_society, name='join_society'),
    path('<int:society_id>/applications/', view_applications, name='view_applications'),
    path('<int:society_id>/applications/<int:application_id>/<str:decision>/', decide_application, name='decide_application'),
]