# Create your views here.
from django.shortcuts import render
from .models import Project

# make views for individual projects
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    return render(request, 'personal/project_detail.html', {'project': project})

# show all projects
def home(request):
    projects = Project.objects.all()
    return render(request, 'personal/home.html', {'projects': projects})