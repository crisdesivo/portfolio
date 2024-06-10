# Create your views here.
from django.shortcuts import render
from .models import Project

def home(request):
    projects = Project.objects.all()
    return render(request, 'personal/home.html', {'projects': projects})