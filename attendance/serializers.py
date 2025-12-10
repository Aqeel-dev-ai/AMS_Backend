from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Attendance, AttendanceBreak
from .utils import format_duration_as_hms


class AttendanceBreakSerializer(serializers.ModelSerializer):
    """
    Serializer for AttendanceBreak model.
    """
    duration = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AttendanceBreak
        fields = ['id', 'break_start', 'break_end', 'duration', 'created_at']
        read_only_fields = ['id', 'created_at', 'duration']
    
    def get_duration(self, obj):
        """Return formatted duration as HH:MM:SS"""
        return obj.duration_display()


class AttendanceSerializer(serializers.ModelSerializer):
    """
    Serializer for Attendance model with nested breaks and camelCase transformation.
    """
    # Additional read-only fields for response
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    profile_picture = serializers.SerializerMethodField(read_only=True)
    
    # Nested breaks
    breaks = AttendanceBreakSerializer(many=True, read_only=True)
    
    # Time fields formatted for display
    start_time_display = serializers.SerializerMethodField(read_only=True)
    end_time_display = serializers.SerializerMethodField(read_only=True)
    total_break_time_display = serializers.SerializerMethodField(read_only=True)
    total_work_time_display = serializers.SerializerMethodField(read_only=True)
    
    # Break info
    breaks_taken = serializers.SerializerMethodField(read_only=True)
    current_break = serializers.SerializerMethodField(read_only=True)
    
    # Write fields (accept camelCase from frontend)
    startTime = serializers.DateTimeField(source='start_time', write_only=True, required=False)
    endTime = serializers.DateTimeField(source='end_time', write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'user', 'user_id', 'user_name', 'profile_picture',
            'date', 'start_time', 'end_time', 'status',
            'breaks',  # Nested breaks array
            'total_break_time', 'total_work_time',
            'start_time_display', 'end_time_display',
            'total_break_time_display', 'total_work_time_display',
            'breaks_taken', 'current_break',
            # Write-only camelCase fields
            'startTime', 'endTime'
        ]
        read_only_fields = ['id', 'user_id', 'user_name', 'profile_picture', 
                           'total_break_time', 'total_work_time', 'breaks']
    
    def get_profile_picture(self, obj):
        """Return profile picture URL"""
        if obj.user.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.profile_picture.url)
        return None
    
    def get_total_break_time_display(self, obj):
        """Format total break time as HH:MM:SS"""
        return format_duration_as_hms(obj.total_break_time)
    
    def get_total_work_time_display(self, obj):
        """Format total work time as HH:MM:SS"""
        return format_duration_as_hms(obj.total_work_time)
    
    def get_start_time_display(self, obj):
        """Return start time as HH:MM:SS"""
        if obj.start_time:
            return obj.start_time.strftime('%H:%M:%S')
        return None

    def get_end_time_display(self, obj):
        """Return end time as HH:MM:SS"""
        if obj.end_time:
            return obj.end_time.strftime('%H:%M:%S')
        return None
    
    def get_breaks_taken(self, obj):
        """Return number of breaks taken"""
        return obj.breaks.count()
    
    def get_current_break(self, obj):
        """Return current running break data or None"""
        current_break = obj.get_current_running_break()
        if current_break:
            return AttendanceBreakSerializer(current_break).data
        return None
    
    def validate(self, data):
        """Validate attendance data"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        # If updating, get existing values
        if self.instance:
            start_time = start_time or self.instance.start_time
            end_time = end_time or self.instance.end_time
        
        # Validate end_time is after start_time
        if end_time and start_time and end_time <= start_time:
            raise serializers.ValidationError({
                'endTime': 'End time must be after start time.'
            })
        
        return data


class StartDaySerializer(serializers.Serializer):
    """Serializer for start_day action"""
    timestamp = serializers.DateTimeField()
    
    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value


class EndDaySerializer(serializers.Serializer):
    """Serializer for end_day action"""
    timestamp = serializers.DateTimeField()
    
    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value


class StartBreakSerializer(serializers.Serializer):
    """Serializer for start_break action"""
    timestamp = serializers.DateTimeField()
    
    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value


class EndBreakSerializer(serializers.Serializer):
    """Serializer for end_break action"""
    timestamp = serializers.DateTimeField()
    
    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value
