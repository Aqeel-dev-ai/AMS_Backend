from django.contrib import admin
from .models import Team, Project, Task


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'team_lead', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'team_lead__email']
    filter_horizontal = ['members']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'client', 'team', 'status', 'created_at')
    list_filter = ('status', 'team', 'created_at')
    search_fields = ('name', 'client', 'description')
    autocomplete_fields = ['team']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title', 'project', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
