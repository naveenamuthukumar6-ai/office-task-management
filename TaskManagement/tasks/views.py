from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Task


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
    user = request.user

    # -------- ROLE BASED TASK VIEW --------
    if user.is_superuser:
        tasks = Task.objects.all()
    else:
        tasks = Task.objects.filter(assigned_to=user)

    # ---------- FILTERS ----------
    assigned_user = request.GET.get('user')
    status = request.GET.get('status')
    date = request.GET.get('date')
    task_name = request.GET.get('task')

    if user.is_superuser and assigned_user:
        tasks = tasks.filter(assigned_to__username__icontains=assigned_user)

    if status:
        tasks = tasks.filter(status=status)

    if date:
        tasks = tasks.filter(created_at__date=date)

    if task_name:
        tasks = tasks.filter(title__icontains=task_name)

    # ---------- COUNTS ----------
    pending = tasks.filter(status='Pending').count()
    progress = tasks.filter(status='In Progress').count()
    completed = tasks.filter(status='Completed').count()

    context = {
        'tasks': tasks,
        'pending': pending,
        'progress': progress,
        'completed': completed,
        'is_admin': user.is_superuser,
    }

    return render(request, 'tasks/dashboard.html', context)

@login_required
@login_required
def add_task(request):
    if not request.user.is_superuser:
        return redirect('dashboard')

    users = User.objects.filter(is_superuser=False)
    tasks = Task.objects.all()

    # ---------- FILTERS ----------
    assigned_user = request.GET.get('user')
    status = request.GET.get('status')
    date = request.GET.get('date')
    title = request.GET.get('title')

    if assigned_user:
        tasks = tasks.filter(assigned_to__id=assigned_user)

    if status:
        tasks = tasks.filter(status=status)

    if date:
        tasks = tasks.filter(due_date=date)

    if title:
        tasks = tasks.filter(title__icontains=title)

    # ---------- ADD TASK ----------
    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            assigned_to=User.objects.get(id=request.POST['assigned_to']),
            due_date=request.POST['due_date'],
            status='Pending'
        )
        return redirect('add_task')

    return render(request, 'tasks/addtask.html', {
        'users': users,
        'tasks': tasks
    })

@login_required
def update_status(request, task_id):
    task = Task.objects.get(id=task_id)

    # 🚫 Employee can update ONLY their task
    if task.assigned_to != request.user:
        return redirect('dashboard')

    # 🚫 LOCK THE TASK IF COMPLETED
    if task.status == 'Completed':
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # ✅ Allow only valid forward statuses
        if new_status in ['Pending', 'In Progress', 'Completed']:
            task.status = new_status
            task.save()

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
def logout_view(request):
    logout(request)
    return redirect('login')
