from django.db import models
from django.conf import settings
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=255)
    team_lead = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True, blank=True, related_name='teams_lead')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='teams',blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-created_at']

class Project(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete'),
    ]

    name = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='not_started')
    team = models.ForeignKey(Team,on_delete=models.SET_NULL,null=True,blank=True,related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.client}"
    class Meta:
        ordering = ['-created_at']

class Task(models.Model):
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

    project = models.ForeignKey(Project,on_delete=models.CASCADE,related_name='tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='created_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='todo')
    priority = models.CharField(max_length=20,choices=PRIORITY_CHOICES,default='medium')
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.project.name}"

    class Meta:
        ordering = ['-created_at']
