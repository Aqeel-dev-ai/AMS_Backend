from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.enum import UserRole
from .models import Attendance, AttendanceBreak
from .serializers import (
    AttendanceSerializer,
    AttendanceBreakSerializer,
    StartDaySerializer,
    EndDaySerializer,
    StartBreakSerializer,
    EndBreakSerializer
)
from .permissions import IsOwnerOrAdmin, IsAdminOrTeamLead, IsAdminOnly


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance management with unlimited breaks support.
    
    Permissions:
    - Admin: View all
    - Team Lead: View own + team members
    - Employee: View own only
    """
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'status', 'user']
    search_fields = ['user__email', 'user__full_name']
    ordering_fields = ['date', 'start_time']
    ordering = ['-date', '-start_time']
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        qs = Attendance.objects.all()
        
        if user.role == UserRole.ADMIN:
            # Admin sees all
            return qs
        elif user.role == UserRole.TEAM_LEAD:
            # Team lead sees own + team members
            from projects.models import Team
            led_teams = Team.objects.filter(team_lead=user)
            team_member_ids = []
            for team in led_teams:
                team_member_ids.extend(team.members.values_list('id', flat=True))
            # Include self
            team_member_ids.append(user.id)
            return qs.filter(user_id__in=team_member_ids)
        else:
            # Employee sees only own
            return qs.filter(user=user)
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['start_day', 'end_day', 'start_break', 'end_break', 'status']:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOwnerOrAdmin()]
    
    @action(detail=False, methods=['post'])
    def start_day(self, request):
        """
        Start work day (clock in) for the current user.
        """
        serializer = StartDaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        timestamp = serializer.validated_data['timestamp']
        date = timestamp.date()
        
        # Check if already started day today
        if Attendance.objects.filter(user=request.user, date=date).exists():
            return Response(
                {'error': 'You have already started your work day today.'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create attendance record
        attendance = Attendance.objects.create(
            user=request.user,
            date=date,
            start_time=timestamp
        )
        
        # Return full attendance record
        response_serializer = AttendanceSerializer(attendance, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def end_day(self, request):
        """
        End work day (clock out) for the current user.
        Auto-calculates total_break_time and total_work_time.
        """
        serializer = EndDaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        timestamp = serializer.validated_data['timestamp']
        date = timestamp.date()
        
        # Get today's attendance record
        try:
            attendance = Attendance.objects.get(user=request.user, date=date)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'You have not started your work day today.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already ended day
        if attendance.end_time:
            return Response(
                {'error': 'You have already ended your work day today.'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Check if there's a running break
        current_break = attendance.get_current_running_break()
        if current_break:
            return Response(
                {'error': 'You must end your current break before ending the work day.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate end time is after start time
        if timestamp <= attendance.start_time:
            return Response(
                {'error': 'End time must be after start time.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update attendance record
        attendance.end_time = timestamp
        attendance.save()  # This will auto-calculate total_break_time and total_work_time
        
        # Return updated attendance record
        response_serializer = AttendanceSerializer(attendance, context={'request': request})
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['post'])
    def start_break(self, request):
        """
        Start a break for the current user.
        Supports unlimited breaks - automatically creates a new AttendanceBreak record.
        """
        serializer = StartBreakSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        timestamp = serializer.validated_data['timestamp']
        date = timestamp.date()
        
        # Get today's attendance record
        try:
            attendance = Attendance.objects.get(user=request.user, date=date)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'You have not started your work day today.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already ended day
        if attendance.end_time:
            return Response(
                {'error': 'You have already ended your work day. Cannot start a break.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already a running break
        current_break = attendance.get_current_running_break()
        if current_break:
            return Response(
                {'error': 'You already have an active break. Please end it first.'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Validate break start is after work day start
        if timestamp <= attendance.start_time:
            return Response(
                {'error': 'Break start time must be after work day start time.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new break record
        new_break = AttendanceBreak.objects.create(
            attendance=attendance,
            break_start=timestamp
        )
        
        # Return updated attendance record with new break
        response_serializer = AttendanceSerializer(attendance, context={'request': request})
        return Response({
            'message': 'Break started successfully.',
            'break_id': new_break.id,
            'attendance': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def end_break(self, request):
        """
        End the current running break for the current user.
        Automatically closes the break that has a start but no end.
        """
        serializer = EndBreakSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        timestamp = serializer.validated_data['timestamp']
        date = timestamp.date()
        
        # Get today's attendance record
        try:
            attendance = Attendance.objects.get(user=request.user, date=date)
        except Attendance.DoesNotExist:
            return Response(
                {'error': 'You have not started your work day today.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the current running break
        current_break = attendance.get_current_running_break()
        if not current_break:
            return Response(
                {'error': 'You do not have an active break to end.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate break end is after break start
        if timestamp <= current_break.break_start:
            return Response(
                {'error': 'Break end time must be after break start time.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update break end time
        current_break.break_end = timestamp
        current_break.save()
        
        # Recalculate attendance totals
        attendance.save()  # This will auto-calculate total_break_time
        
        # Return updated attendance record
        response_serializer = AttendanceSerializer(attendance, context={'request': request})
        return Response({
            'message': 'Break ended successfully.',
            'break_id': current_break.id,
            'attendance': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get current work day status for the user.
        """
        today = timezone.now().date()
        
        try:
            attendance = Attendance.objects.get(user=request.user, date=today)
            
            current_break = attendance.get_current_running_break()
            breaks_taken = attendance.breaks.count()
            
            return Response({
                'isDayStarted': True,
                'startTime': attendance.start_time.isoformat(),
                'isDayEnded': attendance.end_time is not None,
                'endTime': attendance.end_time.isoformat() if attendance.end_time else None,
                'isOnBreak': current_break is not None,
                'currentBreak': AttendanceBreakSerializer(current_break).data if current_break else None,
                'breaksTaken': breaks_taken,
                'totalBreakTime': AttendanceSerializer().get_total_break_time_display(attendance),
                'totalWorkTime': AttendanceSerializer().get_total_work_time_display(attendance)
            })
        except Attendance.DoesNotExist:
            return Response({
                'isDayStarted': False,
                'startTime': None,
                'isDayEnded': False,
                'endTime': None,
                'isOnBreak': False,
                'currentBreak': None,
                'breaksTaken': 0,
                'totalBreakTime': '00:00:00',
                'totalWorkTime': None
            })
