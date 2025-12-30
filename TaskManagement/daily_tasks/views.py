from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DailyTask
from accounts.decorators import role_required
from notifications.models import Notification


@login_required
def dashboard(request):
    role = request.user.userprofile.role.role_code

    if role in ['ADMIN', 'MANAGER']:
        tasks = DailyTask.objects.all()
    else:
        tasks = DailyTask.objects.filter(user=request.user)

    return render(request, "daily_tasks/dashboard.html", {
        "tasks": tasks.order_by('-date'),
        "role": role
    })


@login_required
def daily_task_list(request):
    role = request.user.userprofile.role.role_code

    if role in ['ADMIN', 'MANAGER']:
        tasks = DailyTask.objects.all()
    else:
        tasks = DailyTask.objects.filter(user=request.user)

    selected_user = request.GET.get('user')
    selected_status = request.GET.get('status')
    selected_date = request.GET.get('date')

    if role in ['ADMIN', 'MANAGER']:
        if selected_user:
            tasks = tasks.filter(user__id=selected_user)
        if selected_status:
            tasks = tasks.filter(status=selected_status)
        if selected_date:
            tasks = tasks.filter(date=selected_date)

    # SAME access for Admin & Manager
    users = User.objects.filter(userprofile__role__role_code='EMPLOYEE')

    return render(request, 'daily_tasks/daily_task_list.html', {
        'tasks': tasks.order_by('-date'),
        'users': users,
        'selected_user': selected_user,
        'selected_status': selected_status,
        'selected_date': selected_date,
        'role': role,
    })


@role_required(['EMPLOYEE'])
@login_required
def add_daily_task(request):
    tasks = DailyTask.objects.filter(user=request.user).order_by('-date')

    if request.method == 'POST':
        task = DailyTask.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            status=request.POST.get('status')
        )

        manager = request.user.userprofile.manager
        if manager:
            Notification.objects.create(
                user=manager,
                message=f"{request.user.username} submitted a daily task: {task.title}"
            )

        return redirect('add_daily_task')

    return render(request, 'daily_tasks/add_daily_task.html', {'tasks': tasks})


@login_required
def edit_daily_task(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)

    if task.user != request.user or task.status == "Completed":
        return redirect('daily_task_list')

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.status = request.POST.get('status')
        task.save()
        return redirect('daily_task_list')

    return render(request, 'daily_tasks/edit_daily_task.html', {'task': task})


@role_required(['EMPLOYEE'])
@login_required
def update_daily_task_status(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)

    if task.user != request.user or task.status == "Completed":
        return redirect('daily_task_list')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        task.status = new_status
        task.save()

        manager = request.user.userprofile.manager
        if manager:
            Notification.objects.create(
                user=manager,
                message=f"{request.user.username} updated task '{task.title}' status to {new_status}"
            )

    return redirect('daily_task_list')

@login_required
def update_task_remarks(request, task_id):
    task = get_object_or_404(DailyTask, id=task_id)

    role = request.user.userprofile.role.role_code

    if role not in ['ADMIN', 'MANAGER']:
        return HttpResponseForbidden("You cannot add remarks")

    if request.method == "POST":
        task.remarks = request.POST.get("remarks")
        task.save()

    return redirect('daily_task_list')

