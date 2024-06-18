# Register your models here.
from django.contrib import admin
from .models import Project
from .models import RecursiveList

admin.site.register(Project)
admin.site.register(RecursiveList)