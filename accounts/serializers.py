from rest_framework import serializers
from accounts.models import User
from accounts.utils import generate_random_password, send_welcome_email

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CreateUserSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    Automatically generates a password and sends it via email.
    """
    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'designation', 'username', 'profile_picture']
        extra_kwargs = {
            'username': {'required': False},
            'profile_picture': {'required': False},
        }
    
    def create(self, validated_data):
        # Generate a random password
        password = generate_random_password()
        
        # Create the user with the generated password
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            full_name=validated_data.get('full_name', ''),
            role=validated_data['role'],
            designation=validated_data.get('designation'),
            username=validated_data.get('username'),
            profile_picture=validated_data.get('profile_picture'),
        )
        
        # Send welcome email with credentials
        email_sent = send_welcome_email(
            user_email=user.email,
            user_name=user.full_name or user.email,
            password=password
        )
        
        # Store email status in the instance (not in DB, just for response)
        user.email_sent = email_sent
        
        return user

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