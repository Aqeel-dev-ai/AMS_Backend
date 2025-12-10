from rest_framework import serializers
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    Excludes sensitive fields like role, is_staff, is_superuser.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'full_name', 'profile_picture', 'designation']
        read_only_fields = ['id', 'email'] 
        
class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)