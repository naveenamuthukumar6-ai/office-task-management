from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import DailyTask


@login_required
def daily_task_list(request):
    user = request.user

    # ---------- SAVE REMARKS (ADMIN ONLY) ----------
    if request.method == "POST" and user.is_staff:
        task_id = request.POST.get('task_id')
        remarks = request.POST.get('remarks')

        task = get_object_or_404(DailyTask, id=task_id)
        task.remarks = remarks
        task.save()

        return redirect('daily_task_list')

    # ---------- BASE QUERY ----------
    if user.is_staff:
        tasks = DailyTask.objects.all().order_by('-date')
    else:
        tasks = DailyTask.objects.filter(user=user).order_by('-date')

    # ---------- FILTERS (ADMIN ONLY) ----------
    selected_user = request.GET.get('user')
    selected_status = request.GET.get('status')
    selected_date = request.GET.get('date')

    if user.is_staff:
        if selected_user:
            tasks = tasks.filter(user__id=selected_user)

        if selected_status:
            tasks = tasks.filter(status=selected_status)

        if selected_date:
            tasks = tasks.filter(date=selected_date)

    return render(request, 'daily_tasks/daily_task_list.html', {
        'tasks': tasks,
        'is_admin': user.is_staff,
        'users': User.objects.filter(is_staff=False),
        'selected_user': selected_user,
        'selected_status': selected_status,
        'selected_date': selected_date,
    })


@login_required
def add_daily_task(request):
    if request.user.is_staff:
        return redirect('daily_task_list')

    if request.method == 'POST':
        DailyTask.objects.create(
            user=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            status=request.POST.get('status'),
        )
        return redirect('daily_task_list')

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
