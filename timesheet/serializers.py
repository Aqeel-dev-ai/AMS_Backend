from rest_framework import serializers
from django.utils import timezone
from datetime import datetime
from .models import TimeEntry


class TimeEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for TimeEntry model with camelCase transformation.
    """
    # Additional read-only fields for response
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    task_description = serializers.CharField(source='task', read_only=True)
    project_id = serializers.IntegerField(source='project.id', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True, allow_null=True)
    project_details = serializers.SerializerMethodField(read_only=True)
    duration_formatted = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = TimeEntry
        fields = [
            'id', 'user', 'user_id', 'task', 'task_description', 
            'project', 'project_id', 'project_name', 'project_details',
            'start_time', 'end_time', 'duration', 'duration_formatted',
            'date', 'is_running', 'status'
        ]
        read_only_fields = ['user', 'duration', 'date']
    
    def to_internal_value(self, data):
        internal_data = {}
        
        field_mapping = {
            'projectId': 'project',
            'startTime': 'start_time',
            'endTime': 'end_time',
            'taskDescription': 'task',
        }
        
        for key, value in data.items():
            if key in field_mapping:
                mapped_key = field_mapping[key]
                
                if key == 'projectId' and value is not None:
                    from projects.models import Project
                    try:
                        internal_data['project'] = Project.objects.get(id=value)
                    except Project.DoesNotExist:
                        raise serializers.ValidationError({'projectId': 'Project not found.'})
                elif key == 'projectId' and value is None:
                    internal_data['project'] = None
                else:
                    internal_data[mapped_key] = value
            else:
                internal_data[key] = value
        
        return super().to_internal_value(internal_data)
    
    def get_project_details(self, obj):
        """Return project details with name and color"""
        if obj.project:
            return {
                'name': obj.project.name,
                'color': 'orange'  # You can add a color field to Project model later
            }
        return None
    
    def get_duration_formatted(self, obj):
        """Format duration as 'Xh Ym' or minutes"""
        if obj.duration:
            total_minutes = int(obj.duration.total_seconds() / 60)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        elif obj.is_running:
            # Calculate elapsed time for running timer
            elapsed = obj.elapsed_minutes
            hours = elapsed // 60
            minutes = elapsed % 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "0m"
    
    def validate(self, data):
        """Validate time entry data"""
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
    
    def create(self, validated_data):
        """Set user from request context"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class StartTimerSerializer(serializers.Serializer):
    """Serializer for starting a timer"""
    task = serializers.CharField(max_length=255)
    projectId = serializers.IntegerField(required=False, allow_null=True)
    startTime = serializers.DateTimeField()
    status = serializers.CharField(required=False, default='in_progress')
    
    def validate_startTime(self, value):
        """Ensure start time is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("Start time cannot be in the future.")
        return value
    
    def validate(self, data):
        """Validate project exists if provided"""
        if data.get('projectId'):
            from projects.models import Project
            try:
                project = Project.objects.get(id=data['projectId'])
                data['project'] = project
            except Project.DoesNotExist:
                raise serializers.ValidationError({'projectId': 'Project not found.'})
        return data


class StopTimerSerializer(serializers.Serializer):
    """Serializer for stopping a timer"""
    endTime = serializers.DateTimeField()
    
    def validate_endTime(self, value):
        """Ensure end time is not in the future"""
        if value > timezone.now():
            raise serializers.ValidationError("End time cannot be in the future.")
        return value


class TimerStateSerializer(serializers.Serializer):
    """Serializer for timer state response"""
    isRunning = serializers.BooleanField()
    task = serializers.CharField(required=False, allow_null=True)
    projectId = serializers.IntegerField(required=False, allow_null=True)
    startTime = serializers.DateTimeField(required=False, allow_null=True)
    elapsed = serializers.IntegerField(required=False)  # minutes
