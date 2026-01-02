from django.db import models
from accounts.models import User
from django.utils import timezone
from config.enums import LeaveType, LeaveStatus

class Leave(models.Model):   
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leaves')
    applied_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='applied_leaves')
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=LeaveStatus.choices, default=LeaveStatus.PENDING)
    admin_comment = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.leave_type} ({self.start_date} to {self.end_date})"

    class Meta:
        ordering = ['-applied_at']
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'