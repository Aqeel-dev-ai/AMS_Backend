from django.contrib import admin
from .models import Leave

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'applied_by',
        'leave_type',
        'start_date',
        'end_date',
        'status',
        'applied_at',
    )
    list_filter = (
        'leave_type',
        'status',
        'start_date',
        'applied_at',
    )
    search_fields = (
        'user__email',
        'user__full_name',
        'applied_by__email',
        'reason',
    )
    readonly_fields = (
        'applied_at',
        'updated_at',
    )
    date_hierarchy = 'start_date'
    ordering = ('-applied_at',)
    list_per_page = 25