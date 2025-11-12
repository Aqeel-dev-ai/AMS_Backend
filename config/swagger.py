from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AETHER API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url="http://127.0.0.1:8000",
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0)),
] 