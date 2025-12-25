from datetime import timedelta
from django.utils import timezone
from .models import Attendance, AttendanceBreak
from config.enums import AttendanceStatus

def start_attendance(user):
    today = timezone.localdate()
    now = timezone.now()

    attendance, created = Attendance.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            "start_time": now,
            "status": AttendanceStatus.PRESENT,
        }
    )

    return attendance

def start_break(attendance):
    running_break = AttendanceBreak.objects.filter(
        attendance=attendance,
        break_end__isnull=True
    ).exists()

    if running_break:
        return None 

    attendance.status = AttendanceStatus.BREAK
    attendance.save(update_fields=["status"])

    return AttendanceBreak.objects.create(
        attendance=attendance,
        break_start=timezone.now()
    )

def end_break(attendance):
    br = AttendanceBreak.objects.filter(
        attendance=attendance,
        break_end__isnull=True
    ).first()

    if not br:
        return None

    br.break_end = timezone.now()
    br.save(update_fields=["break_end"])

    attendance.status = AttendanceStatus.PRESENT
    attendance.save(update_fields=["status"])

    return br

def end_attendance(attendance):
    attendance.end_time = timezone.now()

    # calculate total break time
    total_break = timedelta(0)
    for br in attendance.breaks.all():
        if br.break_end:
            total_break += (br.break_end - br.break_start)

    total_work = attendance.end_time - attendance.start_time

    attendance.total_break_time = total_break
    attendance.total_work_time = total_work
    attendance.status = AttendanceStatus.OFFLINE

    attendance.save()
    return attendance


# attendance/services.py
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Attendance, AttendanceBreak

def get_attendance_or_error(user, date):
    try:
        return Attendance.objects.get(user=user, date=date)
    except Attendance.DoesNotExist:
        raise ValidationError("You have not started your work day today.")

def get_running_break(attendance):
    return AttendanceBreak.objects.filter(attendance=attendance, break_end__isnull=True).first()

def start_day(user, timestamp):
    date = timestamp.date()
    if Attendance.objects.filter(user=user, date=date).exists():
        raise ValidationError("You have already started your work day today.")
    return Attendance.objects.create(user=user, date=date, start_time=timestamp)

def end_day(user, timestamp):
    attendance = get_attendance_or_error(user, timestamp.date())

    if attendance.end_time:
        raise ValidationError("You have already ended your work day today.")

    if get_running_break(attendance):
        raise ValidationError("You must end your current break before ending the work day.")

    if timestamp <= attendance.start_time:
        raise ValidationError("End time must be after start time.")

    attendance.end_time = timestamp
    attendance.save(update_fields=["end_time"])
    return attendance

def start_break(user, timestamp):
    attendance = get_attendance_or_error(user, timestamp.date())

    if attendance.end_time:
        raise ValidationError("You have already ended your work day. Cannot start a break.")

    if get_running_break(attendance):
        raise ValidationError("You already have an active break. Please end it first.")

    if timestamp <= attendance.start_time:
        raise ValidationError("Break start time must be after work day start time.")

    br = AttendanceBreak.objects.create(attendance=attendance, break_start=timestamp)
    return attendance, br

def end_break(user, timestamp):
    attendance = get_attendance_or_error(user, timestamp.date())

    br = get_running_break(attendance)
    if not br:
        raise ValidationError("You do not have an active break to end.")

    if timestamp <= br.break_start:
        raise ValidationError("Break end time must be after break start time.")

    br.break_end = timestamp
    br.save(update_fields=["break_end"])
    return attendance, br

def get_status(user):
    today = timezone.localdate()
    attendance = Attendance.objects.filter(user=user, date=today).first()
    if not attendance:
        return None, None, 0

    current_break = get_running_break(attendance)
    breaks_taken = attendance.breaks.count()
    return attendance, current_break, breaks_taken
