from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from accounts.serializers import UserSerializer, UserProfileSerializer, ChangePasswordSerializer, CreateUserSerializer
from accounts.models import User
from accounts.enum import UserRole, UserDesignation


class UserView(APIView):
    """
    Get current authenticated user details and update profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': ['Wrong password.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response(
                {'message': 'Password updated successfully.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user operations.
    
    Permissions:
    - Admin: Full CRUD access
    - Others: Read-only access to all users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_serializer_class(self):
        """
        Use CreateUserSerializer for user creation to handle password generation and email.
        Use UserSerializer for other operations.
        """
        if self.action == 'create':
            return CreateUserSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Override create to provide feedback on email sending status.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get the email status from the user instance
        email_sent = getattr(user, 'email_sent', False)
        
        # Use UserSerializer for the response to include all user data
        response_serializer = UserSerializer(user)
        
        response_data = {
            'message': 'User created successfully.',
            'email_sent': email_sent,
            'email_status': 'Email sent successfully with login credentials.' if email_sent else 'User created but email could not be sent. Please share credentials manually.',
            'user': response_serializer.data
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    def get_permissions(self):
        """
        Admin can do everything.
        Regular users can only list and retrieve.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'deactivate', 'reactivate']:
            permission_classes = [permissions.IsAuthenticated, self.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        All authenticated users can see all users (for team creation, etc.)
        """
        return User.objects.all().order_by('-created_at')
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent hard delete. Use deactivate endpoint instead.
        """
        return Response(
            {
                'error': 'Hard delete is not allowed. Use the deactivate endpoint instead.',
                'hint': f'POST /api/v1/accounts/users/{kwargs.get("pk")}/deactivate/'
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Soft delete: Deactivate user by setting is_active to False.
        This prevents login but keeps all user data intact.
        """
        user = self.get_object()
        
        if not user.is_active:
            return Response(
                {'error': 'User is already inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        serializer = self.get_serializer(user)
        return Response({
            'message': 'User deactivated successfully.',
            'user': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def reactivate(self, request, pk=None):
        """
        Reactivate a deactivated user by setting is_active to True.
        """
        user = self.get_object()
        
        if user.is_active:
            return Response(
                {'error': 'User is already active.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = True
        user.save()
        
        serializer = self.get_serializer(user)
        return Response({
            'message': 'User reactivated successfully.',
            'user': serializer.data
        })
    
    class IsAdminUser(permissions.BasePermission):
        """
        Custom permission to only allow admins to edit users.
        """
        def has_permission(self, request, view):
            return request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN


class RegisterView(APIView):
    """
    Register a new user (Admin only).
    Generates password automatically and sends it via email.
    """
    permission_classes = [IsAuthenticated] # We will add custom admin permission check

    def post(self, request):
        # Check for admin permission
        if not (request.user and request.user.is_authenticated and request.user.role == UserRole.ADMIN):
             return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Get the email status from the user instance
            email_sent = getattr(user, 'email_sent', False)
            
            response_data = {
                'message': 'User registered successfully.',
                'email_sent': email_sent,
                'email_status': 'Email sent successfully with login credentials.' if email_sent else 'User registered but email could not be sent. Please share credentials manually.',
                'user': UserSerializer(user).data
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

