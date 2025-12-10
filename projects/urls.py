from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamViewSet, ProjectViewSet, TaskViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
