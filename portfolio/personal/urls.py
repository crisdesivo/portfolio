from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hire_me/', views.hire_me, name='hire_me'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
]
