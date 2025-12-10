from django.contrib import admin
from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'project', 'start_time', 'end_time', 'duration', 'is_running']
    list_filter = ['is_running', 'date', 'project']
    search_fields = ['user__email', 'user__full_name', 'task']
    date_hierarchy = 'date'
    readonly_fields = ['duration', 'date']
    ordering = ['-start_time']
    list_per_page = 50
