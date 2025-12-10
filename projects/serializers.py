from rest_framework import serializers
from django.utils import timezone
from datetime import date
from .models import Team, Project, Task


class TeamSerializer(serializers.ModelSerializer):
    """
    Serializer for Team model.
    Includes nested team lead details (id, full_name, email).
    Only admins can create teams.
    """
    team_lead_details = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_team_lead_details(self, obj):
        """Return team lead details including id, full_name, and email."""
        if obj.team_lead:
            return {
                'id': obj.team_lead.id,
                'full_name': obj.team_lead.full_name,
                'username': obj.team_lead.email, 
                'email': obj.team_lead.email,
            }
        return None


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    Includes team name as a read-only field.
    """
    team_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_team_name(self, obj):
        """Return the name of the team assigned to this project."""
        return obj.team.name if obj.team else None



class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    Includes project_name, assigned_to_name, and created_by_name as read-only fields.
    """
    project_name = serializers.SerializerMethodField(read_only=True)
    assigned_to_name = serializers.SerializerMethodField(read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'        
        read_only_fields = ['created_at', 'updated_at', 'created_by']

    def get_project_name(self, obj):
        """Return the name of the project this task belongs to."""
        return obj.project.name if obj.project else None

    def get_assigned_to_name(self, obj):
        """Return the full name of the user assigned to this task."""
        return obj.assigned_to.full_name if obj.assigned_to else None

    def get_created_by_name(self, obj):
        """Return the full name of the user who created this task."""
        return obj.created_by.full_name if obj.created_by else None

    def validate_due_date(self, value):
        """
        Ensure due_date is not in the past during creation.
        """
        # Only validate for creation, not updates
        if not self.instance and value < date.today():
            raise serializers.ValidationError(
                "Due date cannot be in the past."
            )
        return value

    def validate(self, data):
        """
        Ensure assigned_to user is a member of the team assigned to the project.
        """
        project = data.get('project') or (self.instance.project if self.instance else None)
        assigned_to = data.get('assigned_to') or (self.instance.assigned_to if self.instance else None)
        
        if project and assigned_to:
            # Check if assigned_to user is a member of the project's team
            team_member_ids = project.team.members.values_list('id', flat=True)
            assigned_to_id = assigned_to.id if hasattr(assigned_to, 'id') else assigned_to
            
            if assigned_to_id not in team_member_ids:
                raise serializers.ValidationError({
                    'assigned_to': f"User must be a member of the project's team ({project.team.name})."
                })
        
        return data

    def create(self, validated_data):
        """
        Set created_by to the current user when creating a task.
        """
        # Get the current user from the request context
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
