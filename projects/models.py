from django.db import models
from django.conf import settings
from django.utils import timezone


class Team(models.Model):
    """
    Team model representing a group of users working together.
    Only admins can create teams.
    """
    name = models.CharField(max_length=255)
    team_lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teams_lead',
        help_text='Team lead responsible for this team'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True,
        help_text='Team members'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class Project(models.Model):
    """
    Project model representing a project assigned to a team.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
    ]

    name = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_started'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.client}"

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    """
    Task model representing a task within a project.
    Tasks are assigned to users and tracked with status and priority.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_tasks',
        help_text='User assigned to this task'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text='User who created this task'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    class Meta:
        ordering = ['-created_at']
