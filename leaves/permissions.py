from rest_framework import permissions
from config.enums import UserRole


class RoleBasedLeavePermission(permissions.BasePermission):
    """
    Permission class for Leave management.
    
    Rules:
    - Admin: Full access to all leaves
    - Team Lead: Can view all leaves, approve/reject leaves (except their own)
    - Employee: Can create, view, and edit their own leaves only
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to access the view."""
        user = request.user
        action = view.action

        # Must be authenticated
        if not user or not user.is_authenticated:
            return False

        # Create: All authenticated users can create leaves
        if action == 'create':
            return user.role in [UserRole.EMPLOYEE, UserRole.TEAM_LEAD, UserRole.ADMIN]
        
        # List/Retrieve: All authenticated users can view
        if action in ['list', 'retrieve']:
            return True
        
        # Edit: All authenticated users (object-level check will verify ownership)
        if action == 'edit':
            return True
        
        # Approve/Reject: Only admin and team lead
        if action in ['approve', 'reject']:
            return user.role in [UserRole.ADMIN, UserRole.TEAM_LEAD]
        
        # Update/Delete: Standard permissions (object-level check)
        return True

    def has_object_permission(self, request, view, obj):
        """Check if user has permission to access the specific leave object."""
        user = request.user
        action = view.action

        # Admin has full access
        if user.role == UserRole.ADMIN:
            return True

        # Retrieve/List: Team leads see all, employees see only their own
        if action in ['retrieve', 'list']:
            if user.role == UserRole.TEAM_LEAD:
                return True
            return obj.user == user

        # Approve/Reject: Admin and team lead can approve/reject (but not their own)
        if action in ['approve', 'reject']:
            # Cannot approve/reject your own leave
            if obj.user == user:
                return False
            # Team lead can approve/reject others' leaves
            if user.role == UserRole.TEAM_LEAD:
                return True
            return False

        # Edit: User can edit their own leave, or the person who applied it for them
        if action == 'edit':
            # Can edit if you are the leave owner
            if obj.user == user:
                return True
            # Can edit if you applied it on behalf of someone else
            if hasattr(obj, 'applied_by') and obj.applied_by == user:
                return True
            return False

        # Update/Partial Update: Same as edit
        if action in ['update', 'partial_update']:
            if obj.user == user:
                return True
            if hasattr(obj, 'applied_by') and obj.applied_by == user:
                return True
            return False

        # Destroy: Only the leave owner can delete (if status is pending)
        if action == 'destroy':
            return obj.user == user and obj.status == 'pending'

        # Default: Only allow access to own leaves
        return obj.user == user
