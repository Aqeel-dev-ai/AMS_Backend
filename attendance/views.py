from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from config.enums import UserRole
from .models import Attendance, AttendanceBreak
from .serializers import AttendanceSerializer, AttendanceBreakSerializer
from . import services
from accounts.models import User
from config.enums import AttendanceStatus
from django.utils import timezone
from projects.models import Team
from django.utils.timezone import localtime


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
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"])
    def status(self, request):
        attendance, current_break = services.get_status(request.user)

        if not attendance:
            return Response({
                "isDayStarted": False,
                "isDayEnded": False,
                "isOnBreak": False,
                "status": "offline",
                "startTime": None,
                "endTime": None,
                "currentBreak": None,
            })

        
        return Response({
            "isDayStarted": True,
            "isDayEnded": attendance.end_time is not None,
            "isOnBreak": current_break is not None,
            "status": attendance.status,
            "startTime": localtime(attendance.start_time).strftime("%H:%M:%S"),
            "endTime": localtime(attendance.end_time).strftime("%H:%M:%S") if attendance.end_time else None,
            "currentBreak": AttendanceBreakSerializer(current_break).data if current_break else None,
        })

    @action(detail=False, methods=["get"])
    def team_status(self, request):
        user = request.user
        today = timezone.localdate()
        
        if user.role == UserRole.ADMIN:
            # Admin sees everyone
            user_ids = User.objects.values_list('id', flat=True)
        else:
            # Team Lead and Employee: See all members of teams they belong to
            # Get all teams where user is either team_lead or a member
            teams = Team.objects.filter(
                models.Q(team_lead=user) | models.Q(members=user)
            ).distinct()
            
            # Get all member IDs from these teams
            team_member_ids = set()
            for team in teams:
                team_member_ids.update(team.members.values_list('id', flat=True))
                if team.team_lead:
                    team_member_ids.add(team.team_lead.id)
            
            user_ids = list(team_member_ids)
       
        # Fetch full names from User model for all users
        users = User.objects.filter(id__in=user_ids).values('id', 'full_name')
        full_name_map = {u['id']: u['full_name'] for u in users}
        
        # Fetch attendance records for today
        attendances = Attendance.objects.filter(
            user_id__in=user_ids,
            date=today
        ).values('user_id', 'status')
        
        status_map = {a['user_id']: a['status'] for a in attendances}
        
        result = []
        for uid in user_ids:
            result.append({
                "user_id": uid,
                "status": status_map.get(uid, AttendanceStatus.OFFLINE),
                "full_name": full_name_map.get(uid, "Unknown")
            })
        
        return Response(result)


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

        if attendance.user_id != self.request.user.id:
            raise PermissionError("Not allowed")

        serializer.save()
