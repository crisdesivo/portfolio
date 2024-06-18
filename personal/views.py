# Create your views here.
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Project, RecursiveList
from django.urls import reverse
from .RecursiveLists import RecursiveListPY
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

class RecursiveListForm(forms.ModelForm):
    class Meta:
        model = RecursiveList
        fields = ['title', 'description', 'parent']

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

def new_id(request):
    # find the next id
    new_id = 1
    while RecursiveList.objects.filter(id=new_id):
        new_id += 1
    return HttpResponseRedirect(f'/lists/{new_id}/')

# def add_child(request, id):
#     return HttpResponseRedirect(request.GET.get('next'))

@csrf_exempt
def add_child(request):
    if request.method == 'POST':
        print(request.POST)
        form = RecursiveListForm(request.POST)
        if form.is_valid():
            print('form is valid')
            new_child = form.save()
            return JsonResponse({'success': True, 'name': new_child.title, 'description': new_child.description, 'id': new_child.id})
        else:
            print('form is not valid')
            print(form)
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

# show all lists
def lists(request):
    if request.method == 'POST':
        form = RecursiveListForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recursive_list'))
    else:
        form = RecursiveListForm()
    root_elements = RecursiveList.objects.filter(parent__isnull=True)
    return render(request, 'personal/recursive_lists.html', {'root_elements': root_elements})
    # root = RecursiveList.objects.get(parent=None)
    # root_id = root.id
    # root = RecursiveListPY(root_id)
    # return render(request, 'personal/recursive_lists.html', {'root': root.generate_html()})