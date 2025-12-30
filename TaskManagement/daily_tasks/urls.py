from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_daily_task, name='add_daily_task'),
    path('daily/', views.daily_task_list, name='daily_task_list'),
    path('edit/<int:task_id>/', views.edit_daily_task, name='edit_daily_task'),
    path('daily-task/update-status/<int:task_id>/', views.update_daily_task_status, name='update_daily_task_status'),
    path('update-remarks/<int:task_id>/', views.update_task_remarks, name='update_task_remarks'),

]
