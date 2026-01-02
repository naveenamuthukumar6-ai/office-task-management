from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Task
from accounts.decorators import role_required
from django.db.models import Count
from notifications.models import Notification
from django.http import HttpResponse
import csv


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'tasks/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'tasks/login.html')


# ✅ ADMIN, MANAGER & EMPLOYEE ACCESS

@login_required
@role_required(['ADMIN', 'MANAGER', 'EMPLOYEE'])
def dashboard(request):
    role = request.user.userprofile.role.role_code

    if role in ['ADMIN', 'MANAGER']:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=request.user)

    pending_count = tasks.filter(status='Pending').count()
    inprogress_count = tasks.filter(status='In Progress').count()
    completed_count = tasks.filter(status='Completed').count()

    # ✅ Group by user AND status
    user_task_data = (
        tasks.values('assigned_to__username', 'status')
        .annotate(count=Count('id'))
        .order_by('assigned_to__username')
    )

    return render(request, 'tasks/dashboard.html', {
        'tasks': tasks,
        'role': role,
        'pending_count': pending_count,
        'inprogress_count': inprogress_count,
        'completed_count': completed_count,
        'user_task_data': user_task_data,
    })

@login_required
@role_required(['ADMIN', 'MANAGER'])
def add_task(request):
    user = request.user
    role = user.userprofile.role.role_code

    # ✅ BOTH Admin & Manager see ALL employees
    users = User.objects.filter(userprofile__role__role_code='EMPLOYEE')

    # ✅ BOTH Admin & Manager see ALL tasks
    tasks = Task.objects.all()

    if request.method == 'POST':
        assigned_user = User.objects.get(id=request.POST['assigned_to'])

        task = Task.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            assigned_to=assigned_user,
            assigned_by=user,
            due_date=request.POST['due_date'],
            status='Pending'
        )

        Notification.objects.create(
            user=assigned_user,
            message=f"You have been assigned a new task: {task.title}"
        )

        return redirect('add_task')

    return render(request, 'tasks/addtask.html', {
        'tasks': tasks,
        'users': users
    })


@login_required
def update_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.assigned_to != request.user or task.status == 'Completed':
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')

        if new_status in ['Pending', 'In Progress', 'Completed']:
            task.status = new_status
            task.save()

            if new_status == 'Completed':
                Notification.objects.create(
                    user=task.assigned_by,
                    message=f"{request.user.username} completed task: {task.title}"
                )

    return redirect('dashboard')


# ✅ ADMIN & MANAGER SAME ACCESS
@login_required
def task_list(request):
    role = request.user.userprofile.role.role_code
    user = request.user

    if role in ['ADMIN', 'MANAGER']:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'role': role
    })


# ✅ ADMIN & MANAGER SAME ACCESS
@login_required
@role_required(['ADMIN', 'MANAGER'])
def export_tasks_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="task_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Assigned To', 'Status', 'Due Date', 'Created At'])

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
