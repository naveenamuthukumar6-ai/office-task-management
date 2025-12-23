from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_task_list, name='daily_task_list'),
     path('add/', views.add_daily_task, name='add_daily_task'), 
    path('edit/<int:task_id>/', views.edit_daily_task, name='edit_daily_task'),
]
