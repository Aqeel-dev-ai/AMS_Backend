from django.urls import path, include
from rest_registration.api.views import register
from accounts.views import UserView, UserViewSet, ChangePasswordView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', register, name='register'),
    path('token/generate/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('user/', UserView.as_view(), name='current_user'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('', include(router.urls)),
]
