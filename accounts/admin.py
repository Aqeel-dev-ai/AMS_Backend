from django.contrib import admin
from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','username', 'email', 'full_name', 'role', 'designation', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'designation', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('username', 'email', 'full_name')
    readonly_fields = ('created_at', 'last_login', 'date_joined')
    ordering = ('-created_at',)
    list_per_page = 25
    
    fieldsets = (
        ('Authentication', {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('full_name', 'profile_picture', 'designation')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at')
        }),
    )
    
    filter_horizontal = ('groups', 'user_permissions')
