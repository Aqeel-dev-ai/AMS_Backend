from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TimeEntryViewSet

router = DefaultRouter()
router.register(r'', TimeEntryViewSet, basename='timesheet')

urlpatterns = [
    path('', include(router.urls)),
]
