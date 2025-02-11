from django.urls import path
from .views import societiespage, top_societies
 
urlpatterns = [
    path('', top_societies, name='home'),
    path('societies/', societiespage, name='societiespage'),
    
]