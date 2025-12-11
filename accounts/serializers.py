from rest_framework import serializers
from accounts.models import User
from accounts.utils import generate_random_password, send_credentials_email

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'designation', 'username', 'profile_picture']
        extra_kwargs = {
            'username': {'required': False},
            'profile_picture': {'required': False},
        }

    def create(self, validated_data):
        # Generate secure random password
        password = generate_random_password()

        # Create user (password is hashed automatically by create_user)
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            full_name=validated_data.get('full_name', ''),
            role=validated_data['role'],
            designation=validated_data.get('designation', ''),
            username=validated_data.get('username') or validated_data['email'],  # fallback
            profile_picture=validated_data.get('profile_picture'),
        )

        # Send minimal credentials email and capture status
        email_sent = send_credentials_email(
            user_email=user.email,
            password=password
        )
        
        # Attach email status to user instance (not saved to DB, just for response)
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