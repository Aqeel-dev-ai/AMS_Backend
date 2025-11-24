from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Leave
from .serializers import LeaveSerializer, LeaveActionSerializer
from .permissions import RoleBasedLeavePermission
from .utils import update_leave_status

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated, RoleBasedLeavePermission]

    def get_queryset(self):
        user = self.request.user
        qs = Leave.objects.all()
        if user.role == 'employee':
            return qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        target_user = serializer.validated_data.get('user', None)

        if target_user and target_user != user:
            if user.role in ['admin', 'team_lead']:
                serializer.save(user=target_user, applied_by=user)
            else:
                raise PermissionDenied("You cannot apply leave for another user.")
        else:
            serializer.save(user=user, applied_by=user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        self.check_object_permissions(request, leave)

        action_serializer = LeaveActionSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)
        comment = action_serializer.validated_data.get('comment', '')

        update_leave_status(leave, 'approved', comment=comment)

        return Response({"status": "Leave approved successfully"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        self.check_object_permissions(request, leave)

        action_serializer = LeaveActionSerializer(data=request.data)
        action_serializer.is_valid(raise_exception=True)
        comment = action_serializer.validated_data.get('comment', '')

        update_leave_status(leave, 'rejected', comment=comment)

        return Response({"status": "Leave rejected successfully"})

    @action(detail=True, methods=['patch'])
    def edit(self, request, pk=None):
        leave = self.get_object()
        self.check_object_permissions(request, leave)

        serializer = self.get_serializer(leave, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "Leave updated successfully",
            "data": serializer.data
        })
