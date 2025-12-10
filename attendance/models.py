from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, time


class Attendance(models.Model):
    """
    Attendance model for tracking employee work day with unlimited breaks.
    """
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField(db_index=True)
    start_time = models.DateTimeField(help_text="Work day start time")
    end_time = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Work day end time"
    )
    
    # Auto-calculated fields
    total_break_time = models.DurationField(
        default=timedelta(0),
        help_text="Total duration of all breaks"
    )
    total_work_time = models.DurationField(
        null=True, 
        blank=True,
        help_text="Total work time (end_time - start_time - total_break_time)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present'
    )
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date', '-start_time']
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.user.email} - {self.date} ({self.status})"
    
    def calculate_total_break_time(self):
        """Calculate total break time by summing all completed breaks."""
        total = timedelta(0)
        
        # Sum all completed breaks (those with both start and end times)
        for break_record in self.breaks.filter(break_end__isnull=False):
            total += (break_record.break_end - break_record.break_start)
        
        self.total_break_time = total
        return self.total_break_time
    
    def calculate_total_work_time(self):
        """Calculate total work time: (end_time - start_time) - total_break_time."""
        if not self.end_time or not self.start_time:
            return None
        
        total_time = self.end_time - self.start_time
        self.total_work_time = total_time - self.total_break_time
        return self.total_work_time
    
    def get_current_running_break(self):
        """
        Get the break that is currently running (has start but no end).
        Returns AttendanceBreak object or None if no break is running.
        """
        return self.breaks.filter(break_start__isnull=False, break_end__isnull=True).first()
    
    def mark_late_if_needed(self, late_threshold_time=time(9, 15)):
        """Mark as late if start time is after threshold (default 9:15 AM)"""
        start_time_only = self.start_time.time()
        if start_time_only > late_threshold_time:
            self.status = 'late'
    
    def save(self, *args, **kwargs):
        # Auto-calculate total break time only if instance exists (has PK)
        if self.pk:
            self.calculate_total_break_time()
        
        # Auto-calculate total work time if end_time exists
        if self.end_time:
            self.calculate_total_work_time()
        
        # Auto-mark as late if needed
        if self.status == 'present':
            self.mark_late_if_needed()
        
        super().save(*args, **kwargs)


class AttendanceBreak(models.Model):
    """
    Model for tracking individual breaks within an attendance record.
    Supports unlimited breaks per day.
    """
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name='breaks',
        help_text="The attendance record this break belongs to"
    )
    break_start = models.DateTimeField(help_text="Break start time")
    break_end = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Break end time (null if break is still running)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['break_start']
        verbose_name = 'Attendance Break'
        verbose_name_plural = 'Attendance Breaks'
    
    def __str__(self):
        status = "Running" if not self.break_end else "Completed"
        return f"{self.attendance.user.email} - {self.break_start.strftime('%Y-%m-%d %H:%M')} ({status})"
    
    def duration(self):
        """Calculate break duration if break has ended."""
        if self.break_end and self.break_start:
            return self.break_end - self.break_start
        return None
    
    def duration_display(self):
        """Return formatted duration as HH:MM:SS."""
        dur = self.duration()
        if dur:
            total_seconds = int(dur.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "00:00:00"
