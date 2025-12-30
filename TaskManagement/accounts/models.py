from django.contrib.auth.models import User
from django.db import models

class Role(models.Model):
    role_code = models.CharField(max_length=20, unique=True)  # ADMIN, MANAGER, EMPLOYEE
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    level = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )

    def __str__(self):
        return f"{self.user.username} - {self.role.role_code}"
