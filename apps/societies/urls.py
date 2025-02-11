from django.urls import path
from .views import societiespage, top_societies
 
urlpatterns = [
    path('', top_societies, name='homepage'),
    path('societies/', societiespage, name='societiespage'),
    
]