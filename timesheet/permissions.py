from rest_framework import permissions
from config.enums import UserRole


class IsOwner(permissions.BasePermission):
    """
    Permission class to allow users to access only their own time entries.
    """
    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Users can only access their own time entries
        return obj.user == request.user
    