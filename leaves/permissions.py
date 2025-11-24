from rest_framework import permissions

class RoleBasedLeavePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        action = view.action

        if not user or not user.is_authenticated:
            return False

        if action == 'create':  
            return user.role in ['employee', 'team_lead', 'admin']
        if action in ['list', 'retrieve']:
            return True  

        if action in ['approve', 'reject']:
            return user.role in ['admin', 'team_lead']

        if action == 'edit':
            return True  
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        action = view.action

        if action in ['retrieve', 'list']:
            if user.role in ['admin', 'team_lead']:
                return True
            return obj.user == user

        if action in ['approve', 'reject']:
            if obj.user == user:
                return False
            if user.role in ['admin', 'team_lead']:
                return True
            return False

        if action == 'edit':
            if obj.user == user:
                return True
            if obj.user != user and hasattr(obj, 'applied_by'):
                return obj.applied_by == user  
            return False

        return obj.user == user
