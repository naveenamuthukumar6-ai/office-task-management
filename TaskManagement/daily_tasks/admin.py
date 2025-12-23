from django.contrib import admin
from .models import DailyTask

class DailyTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'date')

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(DailyTask, DailyTaskAdmin)
