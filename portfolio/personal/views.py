# Create your views here.
from django.shortcuts import render
from .models import Project
import json
import os
from django.conf import settings

# TODO use openai?
# TODO upload to cloud run as is to test
# TODO then download from the script https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf
# TODO use llama_cpp python module to load the model
# TODO add a view to interact with the model, a chat
# Google Cloud Run supposedly has 8 GB of storage which should be enough for the 1.3 GB model

# make views for individual projects
def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    return render(request, 'personal/project_detail.html', {'project': project})

# show all projects
def home(request):
    projects = Project.objects.all()
    # sort projects by priority (highest first)
    projects = sorted(projects, key=lambda x: x.priority, reverse=True)
    return render(request, 'personal/home.html', {'projects': projects})

# hire me page
def hire_me(request):
    return render(request, 'personal/hire_me.html', {})
