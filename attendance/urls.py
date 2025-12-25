from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, AttendanceBreakViewSet

router = DefaultRouter()
router.register(r"attendance", AttendanceViewSet, basename="attendance")
router.register(r"attendance-breaks", AttendanceBreakViewSet, basename="attendance-breaks")

urlpatterns = [
    path("", include(router.urls)),
]
