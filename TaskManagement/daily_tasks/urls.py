from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_daily_task, name='add_daily_task'),
    path('daily/', views.daily_task_list, name='daily_task_list'),
    path('edit/<int:task_id>/', views.edit_daily_task, name='edit_daily_task'),
]
