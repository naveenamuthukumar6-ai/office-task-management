from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile, Role


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Get default role (EMPLOYEE)
        employee_role = Role.objects.get(role_code="EMPLOYEE")

        UserProfile.objects.create(
            user=instance,
            role=employee_role
        )