from urllib import request
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DailyTask
from accounts.decorators import role_required
from notifications.models import Notification



@login_required
def daily_task_list(request):
    role = request.user.userprofile.role

    # 🔹 BASE QUERYSET
    if role == 'ADMIN':
        tasks = DailyTask.objects.all()

    else:  # EMPLOYEE
        tasks = DailyTask.objects.filter(user=request.user)

    # 🔹 FILTERS (ADMIN ONLY)
    selected_user = request.GET.get('user')
    selected_status = request.GET.get('status')
    selected_date = request.GET.get('date')

    if role == 'ADMIN':

        if selected_user:
            tasks = tasks.filter(user__id=selected_user)

        if selected_status:
            tasks = tasks.filter(status=selected_status)

        if selected_date:
            tasks = tasks.filter(date=selected_date)

    return render(request, 'daily_tasks/daily_task_list.html', {
        'tasks': tasks.order_by('-date'),
        'users': User.objects.filter(userprofile__role='EMPLOYEE'),
        'selected_user': selected_user,
        'selected_status': selected_status,
        'selected_date': selected_date,
    })

@login_required
@role_required(['EMPLOYEE'])
@login_required
def add_daily_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')

        DailyTask.objects.create(
            user=request.user,
            title=title,
            description=description,
            status=status
        )

        # 🔔 Notify Admin
        admin = User.objects.filter(userprofile__role='ADMIN').first()
        if admin:
            Notification.objects.create(
                user=admin,
                message=f"{request.user.username} submitted a daily task"
            )

        return redirect('daily_task_list')

    # ✅ THIS MUST BE AT FUNCTION LEVEL (NO EXTRA SPACES)
    return render(request, 'daily_tasks/add_daily_task.html')
@login_required
def edit_daily_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)

    if task.user != request.user:
        return redirect('daily_task_list')

    if task.status == "Completed":
        return redirect('daily_task_list')

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.status = request.POST.get('status')
        task.save()

        return redirect('daily_task_list')

    return render(request, 'daily_tasks/edit_daily_task.html', {'task': task})
