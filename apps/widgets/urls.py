from django.urls import path

from .views import *

urlpatterns = [
    path('update_order/<int:society_id>/', update_widget_order, name='update_widget_order'),
]