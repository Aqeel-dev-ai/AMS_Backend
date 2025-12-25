from rest_framework import serializers
from django.utils import timezone
from .models import Attendance, AttendanceBreak
from .utils import format_duration_as_hms


# ---------------------------
# Attendance Break Serializer
# ---------------------------
class AttendanceBreakSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AttendanceBreak
        fields = ["id", "break_start", "break_end", "duration", "created_at"]
        read_only_fields = ["id", "created_at", "duration"]

    def get_duration(self, obj):
        if obj.break_start and obj.break_end:
            seconds = int((obj.break_end - obj.break_start).total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return "00:00:00"


# ---------------------------
# Attendance Serializer
# ---------------------------
class AttendanceSerializer(serializers.ModelSerializer):
    # user info (read-only)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)

    # relations
    breaks = AttendanceBreakSerializer(many=True, read_only=True)

    # display fields
    start_time_display = serializers.SerializerMethodField(read_only=True)
    end_time_display = serializers.SerializerMethodField(read_only=True)
    total_break_time_display = serializers.SerializerMethodField(read_only=True)
    total_work_time_display = serializers.SerializerMethodField(read_only=True)

    breaks_taken = serializers.SerializerMethodField(read_only=True)
    current_break = serializers.SerializerMethodField(read_only=True)

    # write-only camelCase fields for frontend
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

            # user info
            "user_id", "user_name", "profile_picture",

            # attendance info
            "date", "status",

            # nested
            "breaks",

            # display
            "start_time_display",
            "end_time_display",
            "total_break_time_display",
            "total_work_time_display",
            "breaks_taken",
            "current_break",

            # write-only
            "startTime",
            "endTime",
        ]
        read_only_fields = [
            "id",
            "user_id", "user_name", "profile_picture",
            "status",
            "breaks",
            "start_time_display",
            "end_time_display",
            "total_break_time_display",
            "total_work_time_display",
            "breaks_taken",
            "current_break",
        ]

    # ---------- helpers ----------
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
        return obj.start_time.strftime("%H:%M:%S") if obj.start_time else None

    def get_end_time_display(self, obj):
        return obj.end_time.strftime("%H:%M:%S") if obj.end_time else None

    def get_breaks_taken(self, obj):
        return obj.breaks.count()

    def get_current_break(self, obj):
        current = obj.breaks.filter(break_end__isnull=True).first()
        return AttendanceBreakSerializer(current).data if current else None

    # ---------- validation ----------
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


# ---------------------------
# Timestamp serializers (DRY)
# ---------------------------
class _TimestampSerializer(serializers.Serializer):
    timestamp = serializers.DateTimeField()

    def validate_timestamp(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value


class StartDaySerializer(_TimestampSerializer):
    pass


class EndDaySerializer(_TimestampSerializer):
    pass


class StartBreakSerializer(_TimestampSerializer):
    pass


class EndBreakSerializer(_TimestampSerializer):
    pass
