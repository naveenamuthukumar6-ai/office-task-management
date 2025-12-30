from django.db import models
from django.contrib.auth.models import User


class DailyTask(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(
        'tasks.Task',   # 👈 STRING REFERENCE
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    def save(self, *args, **kwargs):
        if self.user.userprofile.role.role_code != 'EMPLOYEE':
            raise ValueError("Only employees can submit daily tasks")
        super().save(*args, **kwargs)
