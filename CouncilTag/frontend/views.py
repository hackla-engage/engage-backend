from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
# Create your views here.
def home_page(request):
    
    return render(request, "index.html", {"settings": settings})