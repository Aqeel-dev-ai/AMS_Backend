from datetime import timedelta
from django.db import models
from django.conf import settings
from config.enums import AttendanceStatus
from django.utils import timezone

class Attendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    total_break_time = models.DurationField(default=timedelta(0))
    total_work_time = models.DurationField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=AttendanceStatus.choices,
        default=AttendanceStatus.OFFLINE
    )

    created_at = timezone.now()
    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "date"],
                name="unique_attendance_per_user_per_day"
            )
        ]

    def __str__(self):
        return f"{self.user.email} - {self.date}"


class AttendanceBreak(models.Model):
    attendance = models.ForeignKey(
        "attendance.Attendance",
        on_delete=models.CASCADE,
        related_name="breaks"
    )

    break_start = models.DateTimeField()
    break_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["break_start"]

    def __str__(self):
        return f"Break - {self.attendance.user.email}"
