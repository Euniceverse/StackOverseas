from django.urls import path
from .views import newspage
 
urlpatterns = [
    path('', newspage, name='newspage'),
]