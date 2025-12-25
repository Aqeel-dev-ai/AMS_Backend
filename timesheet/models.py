from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class TimeEntry(models.Model):
    """
    Time entry model for tracking time spent on tasks/projects.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    task = models.CharField(max_length=255, help_text='Task description')
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    date = models.DateField(db_index=True)
    is_running = models.BooleanField(default=False, db_index=True)
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress'
    )
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Time Entry'
        verbose_name_plural = 'Time Entries'
        indexes = [
            models.Index(fields=['user', 'is_running']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.task} ({self.date})"
    
    @property
    def elapsed_minutes(self):
        """Calculate elapsed time in minutes for running timer"""
        if self.is_running and self.start_time:
            elapsed = timezone.now() - self.start_time
            return int(elapsed.total_seconds() / 60)
        elif self.duration:
            return int(self.duration.total_seconds() / 60)
        return 0
    
    def calculate_duration(self):
        """Calculate duration when timer stops"""
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time
            return self.duration
        return None
    
    def save(self, *args, **kwargs):
        # Auto-set date from start_time
        if self.start_time and not self.date:
            self.date = self.start_time.date()
        
        # Auto-calculate duration if end_time exists
        if self.end_time and not self.is_running:
            self.calculate_duration()
        
        super().save(*args, **kwargs)
