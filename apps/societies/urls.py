from django.urls import path
from .views import societiespage, create_society, top_societies, admin_pending_societies, admin_confirm_society_decision, my_societies, society_admin_view, remove_widget, society_page, update_widget_order

urlpatterns = [
    path('societiespage/', societiespage, name='societiespage'),
    path('my_societies/', my_societies, name='my_societies'),
    path('list/', top_societies, name='top_societies'),    
    path('create/', create_society, name='create_society'),
    path('admin/pending/', admin_pending_societies, name='admin_pending_societies'),
    path('admin/confirm/<int:society_id>/<str:action>/', admin_confirm_society_decision, name='admin_confirm_society_decision'),
    path("<int:society_id>/", society_page, name="society_page"),
    path("<int:society_id>/admin/", society_admin_view, name="society_admin_view"),
    path("<int:society_id>/remove-widget/<int:widget_id>/", remove_widget, name="remove_widget"),
    path("<int:society_id>/update-order/", update_widget_order, name="update_widget_order"),
]