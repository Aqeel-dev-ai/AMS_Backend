from rest_framework import permissions
from accounts.enum import UserRole


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow users to access their own records or admins to access all.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Users can only access their own records
        return obj.user == request.user


class IsAdminOrTeamLead(permissions.BasePermission):
    """
    Permission class for admin and team lead access.
    Team leads can view their team members' records.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin and team lead have access
        return request.user.role in [UserRole.ADMIN, UserRole.TEAM_LEAD]
    
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team lead can access team members' records
        if request.user.role == UserRole.TEAM_LEAD:
            # Check if the user is in a team led by the current user
            from projects.models import Team
            led_teams = Team.objects.filter(team_lead=request.user)
            for team in led_teams:
                if team.members.filter(id=obj.user.id).exists():
                    return True
        
        return False


class IsAdminOnly(permissions.BasePermission):
    """
    Permission class for admin-only access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN
