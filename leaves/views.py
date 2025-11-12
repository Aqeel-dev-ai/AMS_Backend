# leaves/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Leave
from .serializers import LeaveSerializer


class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'admin':
            return Leave.objects.all()

        elif user.role == 'team_lead':
            return Leave.objects.all()
        else: 
            return Leave.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['employee', 'team_lead']:
            raise serializer.ValidationError("You are not allowed to apply for leave.")

        serializer.save(user=user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        user = request.user

        if user.role == 'admin':
            pass
        elif user.role == 'team_lead':
            if leave.user.role != 'employee':
                return Response(
                    {"error": "Team Lead can only approve Employee leaves"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        if leave.status != 'pending':
            return Response(
                {"error": f"Cannot approve a leave that is already {leave.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.status = 'approved'
        leave.admin_comment = request.data.get('comment', '')
        leave.save()

        return Response({"status": "Leave approved successfully"})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        user = request.user

        if user.role == 'admin':
            pass
        elif user.role == 'team_lead':
            if leave.user.role != 'employee':
                return Response(
                    {"error": "Team Lead can only reject Employee leaves"},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        if leave.status != 'pending':
            return Response(
                {"error": f"Cannot reject a leave that is already {leave.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        leave.status = 'rejected'
        leave.admin_comment = request.data.get('comment', '')
        leave.save()

        return Response({"status": "Leave rejected successfully"})

    @action(detail=True, methods=['patch'], url_path='edit')
    def edit(self, request, pk=None):
        leave = self.get_object()
        user = request.user

        if leave.status != 'pending':
            return Response(
                {"error": "Only pending leaves can be edited"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Owner (who applied) can edit
        if leave.user == user:
            pass
        else:
            return Response(
                {"error": "You do not have permission to edit this leave"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Partial update
        serializer = self.get_serializer(leave, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "Leave updated successfully",
            "data": serializer.data
        })