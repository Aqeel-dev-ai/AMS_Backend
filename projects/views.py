from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Team, Project, Task
from .serializers import TeamSerializer, ProjectSerializer, TaskSerializer
from .permissions import TeamPermission, ProjectPermission, TaskPermission


class TeamViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Team model.
    Provides CRUD operations for teams with role-based permissions.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [TeamPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['team_lead', 'name']
    search_fields = ['name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter queryset based on user role.
        - Admin: sees all teams
        - Team Lead: sees teams they lead or are members of
        - Employee: sees only teams they are members of
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin sees all teams
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        
        # Team Lead sees teams they lead or are members of
        if hasattr(user, 'role') and user.role == 'team_lead':
            return queryset.filter(
                models.Q(team_lead=user) | models.Q(members=user)
            ).distinct()
        
        # Employee sees only teams they are members of
        if hasattr(user, 'role') and user.role == 'employee':
            return queryset.filter(members=user).distinct()
        
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model.
    Provides CRUD operations for projects with role-based permissions.
    Supports filtering by status, client, and team.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [ProjectPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'client', 'team']
    search_fields = ['name', 'client', 'description']
    ordering_fields = ['created_at', 'deadline', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filter queryset based on user role.
        - Admin: sees all projects
        - Team Lead: sees projects for teams they lead or are members of
        - Employee: sees projects for teams they are members of
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin sees all projects
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        
        # Team Lead sees projects for teams they lead or are members of
        if hasattr(user, 'role') and user.role == 'team_lead':
            return queryset.filter(
                models.Q(team__team_lead=user) | models.Q(team__members=user)
            ).distinct()
        
        # Employee sees projects for teams they are members of
        if hasattr(user, 'role') and user.role == 'employee':
            return queryset.filter(team__members=user).distinct()
        
        return queryset


from timesheet.models import TimeEntry
from timesheet.serializers import TimeEntrySerializer

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model (Now served by TimeEntry).
    Provides CRUD operations for tasks (time entries) with role-based permissions.
    """
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [TaskPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'project', 'user']
    search_fields = ['task', 'project__name']
    ordering_fields = ['start_time', 'date', 'status']
    ordering = ['-start_time']

    def get_queryset(self):
        """
        Filter queryset based on user role.
        - Admin: sees all time entries
        - Team Lead: sees all time entries for projects in teams they lead or are members of
        - Employee: sees only their own time entries
        """
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin sees all time entries
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
        
        # Team Lead sees all time entries for projects in teams they lead or are members of
        if hasattr(user, 'role') and user.role == 'team_lead':
            return queryset.filter(
                models.Q(project__team__team_lead=user) | models.Q(project__team__members=user)
            ).distinct()
        
        # Employee sees only their own time entries
        if hasattr(user, 'role') and user.role == 'employee':
            return queryset.filter(user=user).distinct()
        
        return queryset

    def perform_create(self, serializer):
        """
        Set user to the current user when creating a time entry (task).
        """
        serializer.save(user=self.request.user)
