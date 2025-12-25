from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from accounts.enum import UserRole
from .models import Attendance
from .serializers import AttendanceSerializer
from .models import AttendanceBreak
from .serializers import AttendanceBreakSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = Attendance.objects.all()

        if user.role == UserRole.ADMIN:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        # Force attendance to be created for the logged-in user only
        serializer.save(user=self.request.user, status="present")  # or AttendanceStatus.PRESENT



class AttendanceBreakViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceBreakSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = AttendanceBreak.objects.select_related("attendance", "attendance__user")

        if user.role == UserRole.ADMIN:
            return qs
        return qs.filter(attendance__user=user)

    def perform_create(self, serializer):
        attendance = serializer.validated_data["attendance"]

        # Ensure user can only create break for their own attendance
        if attendance.user_id != self.request.user.id:
            raise PermissionError("Not allowed")

        serializer.save()
