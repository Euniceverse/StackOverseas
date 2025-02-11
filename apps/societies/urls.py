from django.urls import path
from .views import societiespage, top_societies
 
urlpatterns = [
    path('', societiespage, name='societiespage'),
    path('list/', top_societies, name='top_societies'),    
]