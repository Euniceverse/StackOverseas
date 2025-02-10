from django.shortcuts import render
from .models import Society
# from django.template.loader import get_template

def societiespage(request):
    # template = get_template('societies.html')
    societies = Society.objects.all()  # Fetch all societies
    return render(request, "societies.html", {'societies': societies})

