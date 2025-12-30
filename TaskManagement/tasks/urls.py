from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-task/', views.add_task, name='add_task'),
    path('update-status/<int:task_id>/', views.update_status, name='update_status'),
    path('logout/', views.logout_view, name='logout'),
    path('tasks/', views.task_list, name='task_list'),
     path('export/tasks/', views.export_tasks_csv, name='export_tasks'),
     
]
