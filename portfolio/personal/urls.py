from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('hire_me/', views.hire_me, name='hire_me'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('ask_question/', views.ask_question, name='ask_question'),
    path('ask_question_openai/', views.ask_question_openai, name='ask_question_openai'),
]
