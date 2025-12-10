from rest_framework import permissions
from accounts.enum import UserRole


class IsAdminUser(permissions.BasePermission):
    """
    Permission class for Admin users.
    Admins have full access to all endpoints.
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users have full access
        return request.user.role == UserRole.ADMIN

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin users have full access to all objects
        return request.user.role == UserRole.ADMIN


class IsTeamLead(permissions.BasePermission):
    """
    Permission class for Team Lead users.
    Team Leads can:
    - Create, Update, Delete Projects for teams they lead
    - Update their own Team details
    - Create, Update, Delete Tasks for their projects
    - Read-only access to other data
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Team leads have read access to all endpoints
        if request.method in permissions.SAFE_METHODS:
            return request.user.role == UserRole.TEAM_LEAD
        
        # For write operations, allow team leads (object-level check will handle specifics)
        return request.user.role == UserRole.TEAM_LEAD

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Team leads have read access to all objects
        if request.method in permissions.SAFE_METHODS:
            return request.user.role == UserRole.TEAM_LEAD
        
        # For Team objects: can update teams they lead
        if obj.__class__.__name__ == 'Team':
            return (request.user.role == UserRole.TEAM_LEAD and 
                    obj.team_lead == request.user)
        
        # For Project objects: can CUD projects for teams they lead
        if obj.__class__.__name__ == 'Project':
            return (request.user.role == UserRole.TEAM_LEAD and 
                    obj.team.team_lead == request.user)
        
        # For Task objects: can CUD tasks for their team's projects
        if obj.__class__.__name__ == 'Task':
            return (request.user.role == UserRole.TEAM_LEAD and 
                    obj.project.team.team_lead == request.user)
        
        return False


class IsTeamMember(permissions.BasePermission):
    """
    Permission class for Team Member (Employee) users.
    Team Members can:
    - Read-only access to Projects assigned to their team
    - Update status of Tasks assigned to them
    - Read-only access to other tasks in their projects
    - Cannot Create or Delete tasks
    """
    def has_permission(self, request, view):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Employees have read access to all endpoints
        if request.method in permissions.SAFE_METHODS:
            return request.user.role == UserRole.EMPLOYEE
        
        # For Task creation/updates, allow (object-level check will handle specifics)
        # Note: Employees cannot create or delete tasks per requirements
        if view.basename == 'task':
            # Allow PATCH/PUT for updating tasks assigned to them
            if request.method in ['PATCH', 'PUT']:
                return request.user.role == UserRole.EMPLOYEE
            # Deny POST and DELETE
            return False
        
        # Deny all other write operations
        return False

    def has_object_permission(self, request, view, obj):
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For Project objects: read-only access to projects assigned to their team
        if obj.__class__.__name__ == 'Project':
            # Check if user is a member of the project's team
            is_team_member = obj.team.members.filter(id=request.user.id).exists()
            if request.method in permissions.SAFE_METHODS:
                return request.user.role == UserRole.EMPLOYEE and is_team_member
            # No write access to projects
            return False
        
        # For Task objects
        if obj.__class__.__name__ == 'Task':
            # Check if user is a member of the project's team
            is_team_member = obj.project.team.members.filter(id=request.user.id).exists()
            
            # Read-only access to tasks in their team's projects
            if request.method in permissions.SAFE_METHODS:
                return request.user.role == UserRole.EMPLOYEE and is_team_member
            
            # Can update only tasks assigned to them (status and other fields)
            if request.method in ['PATCH', 'PUT']:
                return (request.user.role == UserRole.EMPLOYEE and 
                        obj.assigned_to == request.user)
            
            # Cannot create or delete tasks
            return False
        
        # For Team objects: read-only access
        if obj.__class__.__name__ == 'Team':
            if request.method in permissions.SAFE_METHODS:
                return request.user.role == UserRole.EMPLOYEE
            return False
        
        return False


class ProjectPermission(permissions.BasePermission):
    """
    Combined permission class for Project endpoints.
    Checks permissions based on user role.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead can create projects
        if request.user.role == UserRole.TEAM_LEAD:
            return True
        
        # Employee has read-only access
        if request.user.role == UserRole.EMPLOYEE:
            return request.method in permissions.SAFE_METHODS
        
        return False

    def has_object_permission(self, request, view, obj):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead can CUD projects for teams they lead
        if request.user.role == UserRole.TEAM_LEAD:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.team.team_lead == request.user
        
        # Employee has read-only access to their team's projects
        if request.user.role == UserRole.EMPLOYEE:
            if request.method in permissions.SAFE_METHODS:
                return obj.team.members.filter(id=request.user.id).exists()
            return False
        
        return False


class TeamPermission(permissions.BasePermission):
    """
    Combined permission class for Team endpoints.
    Only admins can create teams.
    Team leads can update teams they lead.
    Employees have read-only access.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access (including create)
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead and Employee have read access only
        if request.user.role in [UserRole.TEAM_LEAD, UserRole.EMPLOYEE]:
            return request.method in permissions.SAFE_METHODS
        
        return False

    def has_object_permission(self, request, view, obj):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead can update teams they lead
        if request.user.role == UserRole.TEAM_LEAD:
            if request.method in permissions.SAFE_METHODS:
                return True
            # Can update only if they are the team lead
            return obj.team_lead == request.user
        
        # Employee has read-only access
        if request.user.role == UserRole.EMPLOYEE:
            return request.method in permissions.SAFE_METHODS
        
        return False


class TaskPermission(permissions.BasePermission):
    """
    Combined permission class for Task endpoints.
    Checks permissions based on user role.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead can create/update/delete tasks
        if request.user.role == UserRole.TEAM_LEAD:
            return True
        
        # Employee can read and update (but not create/delete)
        if request.user.role == UserRole.EMPLOYEE:
            if request.method in permissions.SAFE_METHODS:
                return True
            # Allow PATCH/PUT for updates (object-level will check if assigned to them)
            if request.method in ['PATCH', 'PUT']:
                return True
            # Deny POST and DELETE
            return False
        
        return False

    def has_object_permission(self, request, view, obj):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Team Lead can CUD tasks for their team's projects
        if request.user.role == UserRole.TEAM_LEAD:
            if request.method in permissions.SAFE_METHODS:
                return True
            return obj.project.team.team_lead == request.user
        
        # Employee can read tasks in their team's projects
        # and update tasks assigned to them
        if request.user.role == UserRole.EMPLOYEE:
            is_team_member = obj.project.team.members.filter(id=request.user.id).exists()
            
            if request.method in permissions.SAFE_METHODS:
                return is_team_member
            
            # Can update only tasks assigned to them
            if request.method in ['PATCH', 'PUT']:
                return obj.assigned_to == request.user
            
            # Cannot create or delete
            return False
        
        return False
