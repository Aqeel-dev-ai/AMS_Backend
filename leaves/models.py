from django.db import models
from accounts.models import User
from django.utils import timezone

class Leave(models.Model):
    LEAVE_TYPES = (
        ('casual', 'Casual'),
        ('sick', 'Sick'),
        
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_comment = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        permissions = [
            ('can_approve_leave', 'Can approve or reject leave'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.status})"
    @property
    def total_days(self):
        """Number of leave days (inclusive)"""
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        # Validate: end date >= start date
        if self.start_date > self.end_date:
            from django.core.exceptions import ValidationError
            raise ValidationError("End date cannot be before start date.")

    def save(self, *args, **kwargs):
        # Auto-set reviewed_at when status changes to approved/rejected
        if self.status in ['approved', 'rejected'] and not self.reviewed_at:
            self.reviewed_at = timezone.now()
        super().save(*args, **kwargs)