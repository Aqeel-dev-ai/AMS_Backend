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
        'admin_comment',
        'applied_at',
    )
    list_filter = (
        'leave_type',
        'status',
        'applied_at',
    )
    search_fields = (
        'user__username',
        'user__email',
        'reason',
    )
    readonly_fields = (
        'applied_at',
        'updated_at',
    )
    ordering = ('-applied_at',)