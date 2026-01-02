from rest_framework import serializers
from django.utils import timezone
from datetime import date
from django.db.models import Sum
from .models import Team, Project, Task
from timesheet.models import TimeEntry
from django.db import models


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        
        # Team Lead Details
        if instance.team_lead:
            response['team_lead'] = {
                'id': instance.team_lead.id,
                'full_name': instance.team_lead.full_name,
                'username': instance.team_lead.username, 
                'email': instance.team_lead.email,
                'role': instance.team_lead.role,

            }
        
        # Members Details
        members_data = []
        for member in instance.members.all():
            members_data.append({
                'id': member.id,
                'full_name': member.full_name,
                'username': member.username,
                'email': member.email,
                'role': member.role,
                'designation': member.designation,

            })
        response['members'] = members_data
        
        # Team Count (team lead + members)
        team_count = instance.members.count()
        if instance.team_lead:
            team_count += 1
        response['team_count'] = team_count
        
        return response


class ProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField(read_only=True)
    total_time = serializers.SerializerMethodField(read_only=True)
    total_tasks = serializers.SerializerMethodField(read_only=True)
    completed_tasks = serializers.SerializerMethodField(read_only=True)
    in_progress_tasks = serializers.SerializerMethodField(read_only=True)
    user_time_breakdown = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_team_name(self, obj):
        return obj.team.name if obj.team else None

    def get_total_time(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return "0h 0m"

        user = request.user
        time_entries = TimeEntry.objects.filter(project=obj)

        if hasattr(user, 'role') and user.role == 'employee':
            time_entries = time_entries.filter(user=user)
        
        # Calculate total duration
        total_duration = time_entries.aggregate(total=Sum('duration'))['total']
        
        if total_duration:
            total_seconds = int(total_duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        
        return "0h 0m"

    def get_total_tasks(self, obj):
        return TimeEntry.objects.filter(project=obj).count()

    def get_completed_tasks(self, obj):
        return TimeEntry.objects.filter(project=obj, status='completed').count()

    def get_in_progress_tasks(self, obj):
        """Return number of in-progress time entries (tasks) for this project."""
        return TimeEntry.objects.filter(project=obj, status='in_progress').count()

    def get_user_time_breakdown(self, obj):
        """Return time breakdown per user for this project."""
        from django.db.models import Sum
        
        user_times = TimeEntry.objects.filter(project=obj).values(
            'user__id', 'user__full_name', 'user__email'
        ).annotate(
            total_duration=Sum('duration')
        ).order_by('-total_duration')
        
        breakdown = []
        for entry in user_times:
            if entry['total_duration']:
                total_seconds = int(entry['total_duration'].total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                breakdown.append({
                    'user_id': entry['user__id'],
                    'user_name': entry['user__full_name'],
                    'user_email': entry['user__email'],
                    'total_time': f"{hours}h {minutes}m",
                    'total_seconds': total_seconds
                })
        
        return breakdown

    def to_representation(self, instance):
        response = super().to_representation(instance)
        if instance.team:
            response['team'] = TeamSerializer(instance.team).data
        return response


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'        
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def validate_due_date(self, value):
        if not self.instance and value < date.today():
            raise serializers.ValidationError(
                "Due date cannot be in the past."
            )
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
