from django.urls import path

from .views import *

urlpatterns = [
    path('<int:society_id>/remove-widget/<int:widget_id>/', remove_widget, name='remove_widget'),
    path('update_order/<int:society_id>/', update_widget_order, name='update_widget_order'),
]