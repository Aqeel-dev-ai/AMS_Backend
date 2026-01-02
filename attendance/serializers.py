from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Attendance, AttendanceBreak
from .utils import format_duration_as_hms
from config.enums import AttendanceStatus


class AttendanceBreakSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AttendanceBreak
        fields = ["id", "attendance", "break_start", "break_end", "duration", "created_at"]
        read_only_fields = ["id", "created_at", "duration"]

    def get_duration(self, obj):
        if obj.break_start and obj.break_end:
            seconds = int((obj.break_end - obj.break_start).total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return "00:00:00"

    def create(self, validated_data):
        # When creating a break, update attendance status to BREAK
        attendance = validated_data['attendance']
        attendance.status = AttendanceStatus.BREAK
        attendance.save(update_fields=['status'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # When ending a break (setting break_end), update attendance status to PRESENT
        instance = super().update(instance, validated_data)
        if instance.break_end:
            attendance = instance.attendance
            attendance.status = AttendanceStatus.PRESENT
            attendance.save(update_fields=['status'])
        return instance


class AttendanceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    breaks = AttendanceBreakSerializer(many=True, read_only=True)
    start_time_display = serializers.SerializerMethodField(read_only=True)
    end_time_display = serializers.SerializerMethodField(read_only=True)
    total_break_time_display = serializers.SerializerMethodField(read_only=True)
    total_work_time_display = serializers.SerializerMethodField(read_only=True)
    current_break = serializers.SerializerMethodField(read_only=True)
    startTime = serializers.DateTimeField( 
        source="start_time", write_only=True, required=False
    )
    endTime = serializers.DateTimeField(
        source="end_time", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id",
            "user_id", "full_name", "profile_picture",
            "date", "status",
            "breaks",
            "start_time_display",
            "end_time_display",
            "total_break_time_display",
            "total_work_time_display",
            "current_break",
            "startTime",
            "endTime",
        ]
        read_only_fields = [
            "id",
            "user_id", "full_name", "profile_picture",
            "status",
            "breaks",
            "start_time_display",
            "end_time_display",
            "total_break_time_display",
            "total_work_time_display",
            "current_break",
        ]

    def get_profile_picture(self, obj):
        pic = getattr(obj.user, "profile_picture", None)
        if not pic:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(pic.url) if request else pic.url

    def get_total_break_time_display(self, obj):
        return format_duration_as_hms(obj.total_break_time)

    def get_total_work_time_display(self, obj):
        return format_duration_as_hms(obj.total_work_time)

    def get_start_time_display(self, obj):
        if not obj.start_time:
            return None
        local_time = timezone.localtime(obj.start_time)
        return local_time.strftime("%H:%M:%S")

    def get_end_time_display(self, obj):
        if not obj.end_time:
            return None
        local_time = timezone.localtime(obj.end_time)
        return local_time.strftime("%H:%M:%S")

    def get_current_break(self, obj):
        current = obj.breaks.filter(break_end__isnull=True).first()
        return AttendanceBreakSerializer(current).data if current else None

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if self.instance:
            start_time = start_time or self.instance.start_time
            end_time = end_time or self.instance.end_time

        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError({
                "endTime": "End time must be after start time."
            })

        return data

    def _check_leave_status(self, user, date):
        """Check if user has approved leave on given date"""
        from leaves.models import Leave
        
        approved_leave = Leave.objects.filter(
            user=user,
            status='approved',
            start_date__lte=date,
            end_date__gte=date
        ).exists()
        
        return AttendanceStatus.LEAVE if approved_leave else None

    def create(self, validated_data):
        # Check if user is on leave
        user = validated_data.get('user')
        date = validated_data.get('date', timezone.localdate())
        
        leave_status = self._check_leave_status(user, date)
        if leave_status:
            # User has approved leave - prevent attendance creation
            raise serializers.ValidationError({
                "error": "Cannot start attendance. You have an approved leave for this date."
            })
        
        # Set status to PRESENT for normal attendance
        validated_data['status'] = AttendanceStatus.PRESENT
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Update fields
        instance = super().update(instance, validated_data)
        
        # Calculate totals if end_time is set (regardless of leave status)
        if instance.end_time:
            # Calculate totals
            total_break = timedelta(0)
            for br in instance.breaks.all():
                if br.break_end:
                    total_break += (br.break_end - br.break_start)
            
            total_work = instance.end_time - instance.start_time
            instance.total_break_time = total_break
            instance.total_work_time = total_work - total_break
            
            # Check if user is on leave
            leave_status = self._check_leave_status(instance.user, instance.date)
            if leave_status:
                instance.status = leave_status
            else:
                # If end_time is set and not on leave, mark as OFFLINE
                instance.status = AttendanceStatus.OFFLINE
        else:
            # No end_time set - check current status
            leave_status = self._check_leave_status(instance.user, instance.date)
            if leave_status:
                instance.status = leave_status
            else:
                # Check if on break
                has_active_break = instance.breaks.filter(break_end__isnull=True).exists()
                if has_active_break:
                    instance.status = AttendanceStatus.BREAK
                else:
                    instance.status = AttendanceStatus.PRESENT
        
        instance.save()
        return instance
