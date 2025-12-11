from django.contrib import admin
from accounts.models import User
from accounts.utils import generate_random_password, send_credentials_email
from django.contrib import messages


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
            'fields': ('username', 'email')
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

    def save_model(self, request, obj, form, change):
        # Only for NEW users (not when editing)
        if not change:
            # If password is empty or unusable (default in admin)
            if not obj.password or obj.password.startswith('!'):
                password = generate_random_password()
                obj.set_password(password)

                # Save the user first
                super().save_model(request, obj, form, change)

                # Then send email
                success = send_credentials_email(obj.email, password)
                if success:
                    messages.success(request, f"User created! Login credentials sent to {obj.email}")
                else:
                    messages.warning(request, f"User created, but email FAILED to {obj.email}")
                return

        # For updates (editing existing user) — normal behavior
        super().save_model(request, obj, form, change)
