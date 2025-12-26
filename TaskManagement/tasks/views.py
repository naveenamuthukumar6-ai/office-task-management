from asyncio import tasks
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.tasks import task
from .models import Task
from accounts.decorators import role_required
from django.db.models import Count
from daily_tasks.models import DailyTask
import csv
from django.http import HttpResponse
from notifications.models import Notification



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'tasks/login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'tasks/login.html')
@login_required
def dashboard(request):
    role = request.user.userprofile.role

    # 🔹 ROLE BASED TASK FILTER
    if role == 'ADMIN':
        tasks = Task.objects.all()

    else:  # EMPLOYEE
        tasks = Task.objects.filter(assigned_to=request.user)

    # 🔹 STATUS COUNTS
    pending_count = tasks.filter(status='Pending').count()
    inprogress_count = tasks.filter(status='In Progress').count()
    completed_count = tasks.filter(status='Completed').count()

    # 🔹 BAR CHART DATA
    user_task_data = (
        tasks
        .values('assigned_to__username')
        .annotate(count=Count('id'))
    )

    context = {
        'tasks': tasks,
        'role': role,
        'pending_count': pending_count,
        'inprogress_count': inprogress_count,
        'completed_count': completed_count,
        'user_task_data': user_task_data,
    }

    return render(request, 'tasks/dashboard.html', context)

@login_required
@role_required(['ADMIN'])
def add_task(request):
    role = request.user.userprofile.role

    # 🔹 BASE QUERYSET
    tasks = Task.objects.all() if role == 'ADMIN' else Task.objects.filter(assigned_to=request.user)
    users = User.objects.filter(userprofile__role='EMPLOYEE') if role == 'ADMIN' else None

    # 🔹 FILTERS
    assigned_user_id = request.GET.get('user')
    status = request.GET.get('status')
    date = request.GET.get('date')
    title = request.GET.get('title')

    if assigned_user_id:
        tasks = tasks.filter(assigned_to__id=assigned_user_id)

    if status:
        tasks = tasks.filter(status=status)

    if date:
        tasks = tasks.filter(due_date=date)

    if title:
        tasks = tasks.filter(title__icontains=title)

    # 🔹 ADD TASK
    if request.method == 'POST':
        assigned_user_obj = User.objects.get(id=request.POST['assigned_to'])
        task = Task.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            assigned_to=assigned_user_obj,
            assigned_by=request.user,
            due_date=request.POST['due_date'],
            status='Pending'
        )

        # 🔹 CREATE NOTIFICATION
        Notification.objects.create(
            user=assigned_user_obj,
            message=f"You have been assigned a new task: {task.title}"
        )

        return redirect('add_task')

    return render(request, 'tasks/addtask.html', {
        'tasks': tasks,
        'users': users,
    })

@login_required
@login_required
def update_status(request, task_id):
    task = Task.objects.get(id=task_id)

    if task.assigned_to != request.user:
        return redirect('dashboard')

    if task.status == 'Completed':
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in ['Pending', 'In Progress', 'Completed']:
            task.status = new_status
            task.save()

            # ✅ NOTIFICATION (PROPERLY INDENTED)
            if new_status == 'Completed':
                Notification.objects.create(
                    user=task.assigned_by,
                    message=f"{request.user.username} completed task: {task.title}"
                )

    return redirect('dashboard')

@login_required
def task_list(request):
    user = request.user

    # Admin sees all tasks
    if user.is_staff:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user)

    context = {
        'tasks': tasks,
        'is_admin': user.is_staff,
    }

    return render(request, 'tasks/task_list.html', context)

@login_required
@role_required(['ADMIN'])
def export_tasks_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Title',
        'Description',
        'Assigned To',
        'Status',
        'Due Date',
        'Created At'
    ])

    tasks = Task.objects.all()

    for task in tasks:
        writer.writerow([
            task.title,
            task.description,
            task.assigned_to.username,
            task.status,
            task.due_date,
            task.created_at
        ])

    return response


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
