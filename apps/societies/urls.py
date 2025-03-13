from django.urls import path

from .views import *


# from .views import (
#     societiespage, 
#     create_society, 
#     admin_pending_societies, 
#     admin_confirm_society_decision, 
#     my_societies, 
#     manage_society, 
#     update_membership,
#     society_detail,
#     join_society,
#     view_applications,
#     decide_application,
# )
from .functions import top_societies

urlpatterns = [
    path('societiespage/', societiespage, name='societiespage'),
    path('my_societies/', my_societies, name='my_societies'),
    path('manage_societies/', view_manage_societies, name= 'manage_societies'),
    path('all_members/', view_all_members, name= 'all_members'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),

    path('<int:society_id>/manage/', manage_society, name='manage_society'),
    path('<int:society_id>/membership/<int:user_id>/update/', update_membership, name='update_membership'),
    path('<int:society_id>/join/', join_society, name='join_society'),
    path('<int:society_id>/applications/', view_applications, name='view_applications'),
    path('<int:society_id>/applications/<int:application_id>/<str:decision>/', decide_application, name='decide_application'),
    path('societies/society/<int:society_id>/admin-delete/', admin_confirm_delete, name='admin_confirm_delete'),
    path('<int:society_id>/admin/', society_admin_view, name='society_admin_view'),
    path('<int:society_id>/remove-widget/<int:widget_id>/', remove_widget, name='remove_widget'),
    path('<int:society_id>/update-order/', update_widget_order, name='update_widget_order'),
    
    # Catch-all: society public page – must be last!
    path('<int:society_id>/', society_page, name='society_page'),
]