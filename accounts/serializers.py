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
        # Generate secure random password FIRST
        password = generate_random_password()
        email = validated_data['email']

        # TRY TO SEND EMAIL FIRST - before creating user
        # This prevents creating orphaned users when email fails
        email_sent = send_credentials_email(
            user_email=email,
            password=password
        )
        
        # If email fails, raise validation error and DO NOT create user
        if not email_sent:
            raise serializers.ValidationError({
                'email': 'Failed to send credentials email. User not created. Please check email configuration and try again.'
            })

        # Email sent successfully - NOW create the user
        user = User.objects.create_user(
            email=email,
            password=password,
            full_name=validated_data.get('full_name', ''),
            role=validated_data['role'],
            designation=validated_data.get('designation', ''),
            username=validated_data.get('username') or email,  # fallback
            profile_picture=validated_data.get('profile_picture'),
        )
        
        # Attach email status to user instance (for response)
        user.email_sent = True  # We know it's True because we checked above

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