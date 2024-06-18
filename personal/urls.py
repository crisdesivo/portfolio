from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('hire_me/', views.hire_me, name='hire_me'),
    path('lists/', views.lists, name='lists'),
    path('new_id/', views.new_id, name='new_id'),
    path('add_child/', views.add_child, name='add_child'),
]
