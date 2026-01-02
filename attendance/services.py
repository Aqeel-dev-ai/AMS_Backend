from datetime import timedelta
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from .models import Attendance, AttendanceBreak
from config.enums import AttendanceStatus


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
    
    return Attendance.objects.create(
        user=user,
        date=date,
        start_time=timestamp,
        status=AttendanceStatus.PRESENT
    )


def end_day(user, timestamp):
    attendance = get_attendance_or_error(user, timestamp.date())

    if attendance.end_time:
        raise ValidationError("You have already ended your work day today.")

    if get_running_break(attendance):
        raise ValidationError("You must end your current break before ending the work day.")

    if timestamp <= attendance.start_time:
        raise ValidationError("End time must be after start time.")

    # Calculate total break time
    total_break = timedelta(0)
    for br in attendance.breaks.all():
        if br.break_end:
            total_break += (br.break_end - br.break_start)

    total_work = timestamp - attendance.start_time

    attendance.end_time = timestamp
    attendance.total_break_time = total_break
    attendance.total_work_time = total_work - total_break
    attendance.status = AttendanceStatus.OFFLINE
    attendance.save()
    
    return attendance


def start_break(user, timestamp):
    attendance = get_attendance_or_error(user, timestamp.date())

    if attendance.end_time:
        raise ValidationError("You have already ended your work day. Cannot start a break.")

    if get_running_break(attendance):
        raise ValidationError("You already have an active break. Please end it first.")

    if timestamp <= attendance.start_time:
        raise ValidationError("Break start time must be after work day start time.")

    # Update attendance status to BREAK
    attendance.status = AttendanceStatus.BREAK
    attendance.save(update_fields=["status"])

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

    # Update attendance status back to PRESENT
    attendance.status = AttendanceStatus.PRESENT
    attendance.save(update_fields=["status"])
    
    return attendance, br


def get_status(user):
    today = timezone.localdate()
    attendance = Attendance.objects.filter(user=user, date=today).first()
    if not attendance:
        return None, None

    current_break = get_running_break(attendance)
    return attendance, current_break


def handle_approved_leave(leave):
    """
    Handle attendance records when leave is approved.
    Ends any active attendance for dates in leave range and sets status to LEAVE.
    
    Args:
        leave: Leave model instance with user, start_date, and end_date
    """
    from .serializers import AttendanceSerializer
    
    # Get all dates in the leave range
    current_date = leave.start_date
    while current_date <= leave.end_date:
        # Check if there's an attendance record for this date
        attendance = Attendance.objects.filter(
            user=leave.user,
            date=current_date
        ).first()
        
        if attendance:
            # End any active breaks first
            for br in attendance.breaks.filter(break_end__isnull=True):
                br.break_end = timezone.now()
                br.save()
            
            # End the day if it's still active (no end_time)
            # Use the serializer to handle all time calculations
            if not attendance.end_time:
                serializer = AttendanceSerializer(
                    attendance,
                    data={'endTime': timezone.now()},
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                # Day already ended, just update status
                attendance.status = AttendanceStatus.LEAVE
                attendance.save()
        
        current_date += timedelta(days=1)

