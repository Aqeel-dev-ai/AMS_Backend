from django.contrib import admin
from .models import Attendance, AttendanceBreak


class AttendanceBreakInline(admin.TabularInline):
    """
    Inline admin for AttendanceBreak to display breaks within Attendance admin.
    """
    model = AttendanceBreak
    extra = 0
    fields = ('break_start', 'break_end', 'duration_display')
    readonly_fields = ('duration_display',)
    ordering = ('break_start',)
    
    def duration_display(self, obj):
        """Display formatted duration"""
        return obj.duration_display()
    duration_display.short_description = 'Duration'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """
    Admin interface for Attendance model with inline breaks.
    """
    list_display = ('user', 'date', 'start_time', 'end_time', 'status', 
                   'breaks_count', 'total_break_time', 'total_work_time')
    list_filter = ('status', 'date', 'user__role')
    search_fields = ('user__email', 'user__full_name')
    date_hierarchy = 'date'
    readonly_fields = ('total_break_time', 'total_work_time')
    inlines = [AttendanceBreakInline]
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'date', 'status')
        }),
        ('Time Information', {
            'fields': ('start_time', 'end_time')
        }),
        ('Calculated Fields', {
            'fields': ('total_break_time', 'total_work_time'),
            'classes': ('collapse',)
        }),
    )
    
    def breaks_count(self, obj):
        """Display number of breaks taken"""
        return obj.breaks.count()
    breaks_count.short_description = 'Breaks'
    
    def save_model(self, request, obj, form, change):
        """Auto-calculate totals on save"""
        obj.save()


@admin.register(AttendanceBreak)
class AttendanceBreakAdmin(admin.ModelAdmin):
    """
    Admin interface for AttendanceBreak model.
    """
    list_display = ('attendance', 'break_start', 'break_end', 'duration_display', 'created_at')
    list_filter = ('attendance__date', 'attendance__user')
    search_fields = ('attendance__user__email', 'attendance__user__full_name')
    date_hierarchy = 'break_start'
    readonly_fields = ('created_at', 'duration_display')
    
    fieldsets = (
        ('Break Information', {
            'fields': ('attendance', 'break_start', 'break_end')
        }),
        ('Metadata', {
            'fields': ('created_at', 'duration_display'),
            'classes': ('collapse',)
        }),
    )
    
    def duration_display(self, obj):
        """Display formatted duration"""
        return obj.duration_display()
    duration_display.short_description = 'Duration'
