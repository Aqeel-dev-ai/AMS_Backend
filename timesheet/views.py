from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import TimeEntry
from .serializers import (
    TimeEntrySerializer,
    StartTimerSerializer,
    StopTimerSerializer,
    TimerStateSerializer
)
from .permissions import IsOwner


class TimeEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TimeEntry management.
    
    Users can only access their own time entries.
    """
    queryset = TimeEntry.objects.all()
    serializer_class = TimeEntrySerializer
    permission_classes = [IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['date', 'project', 'is_running']
    search_fields = ['task']
    ordering_fields = ['start_time', 'date']
    ordering = ['-start_time']
    
    def get_queryset(self):
        """Users see only their own time entries"""
        return TimeEntry.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Set user from request"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a new timer.
        Stops any currently running timer before starting new one.
        """
        serializer = StartTimerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Stop any currently running timer
        running_timers = TimeEntry.objects.filter(user=request.user, is_running=True)
        for timer in running_timers:
            timer.end_time = timezone.now()
            timer.is_running = False
            timer.save()
        
        # Create new time entry
        time_entry = TimeEntry.objects.create(
            user=request.user,
            task=serializer.validated_data['task'],
            project=serializer.validated_data.get('project'),
            start_time=serializer.validated_data['startTime'],
            is_running=True,
            status=serializer.validated_data.get('status', 'in_progress')
        )
        
        # Return timer state
        return Response({
            'isRunning': True,
            'task': time_entry.task,
            'projectId': time_entry.project.id if time_entry.project else None,
            'startTime': time_entry.start_time.isoformat(),
            'elapsed': 0
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def stop(self, request):
        """
        Stop the currently running timer.
        """
        serializer = StopTimerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get currently running timer
        try:
            time_entry = TimeEntry.objects.get(user=request.user, is_running=True)
        except TimeEntry.DoesNotExist:
            return Response(
                {'error': 'No timer is currently running.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TimeEntry.MultipleObjectsReturned:
            # Handle edge case of multiple running timers
            time_entry = TimeEntry.objects.filter(user=request.user, is_running=True).first()
        
        end_time = serializer.validated_data['endTime']
        
        # Validate end time is after start time
        if end_time <= time_entry.start_time:
            return Response(
                {'error': 'End time must be after start time.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update time entry
        time_entry.end_time = end_time
        time_entry.is_running = False
        time_entry.save()
        
        # Return completed time entry
        response_serializer = TimeEntrySerializer(time_entry, context={'request': request})
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        Get current timer state.
        Returns null if no timer is running.
        """
        try:
            time_entry = TimeEntry.objects.get(user=request.user, is_running=True)
            return Response({
                'isRunning': True,
                'task': time_entry.task,
                'projectId': time_entry.project.id if time_entry.project else None,
                'startTime': time_entry.start_time.isoformat(),
                'elapsed': time_entry.elapsed_minutes
            })
        except TimeEntry.DoesNotExist:
            return Response({
                'isRunning': False,
                'task': None,
                'projectId': None,
                'startTime': None,
                'elapsed': 0
            })
        except TimeEntry.MultipleObjectsReturned:
            # Handle edge case
            time_entry = TimeEntry.objects.filter(user=request.user, is_running=True).first()
            return Response({
                'isRunning': True,
                'task': time_entry.task,
                'projectId': time_entry.project.id if time_entry.project else None,
                'startTime': time_entry.start_time.isoformat(),
                'elapsed': time_entry.elapsed_minutes
            })
