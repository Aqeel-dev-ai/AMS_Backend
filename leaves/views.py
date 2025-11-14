from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Leave
from .serializers import LeaveSerializer
from .permissions import RoleBasedLeavePermission
from .utils import update_leave_status


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated, RoleBasedLeavePermission]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['admin', 'team_lead']:
            return Leave.objects.all()
        return Leave.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        self.check_object_permissions(request, leave)

        update_leave_status(leave, 'approved', comment=request.data.get('comment', ''))

        return Response({"status": "Leave approved successfully"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        self.check_object_permissions(request, leave)

        update_leave_status(leave, 'rejected', comment=request.data.get('comment', ''))

        return Response({"status": "Leave rejected successfully"})

    @action(detail=True, methods=['patch'], url_path='edit')
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
