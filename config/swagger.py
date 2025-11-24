from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="TorchSync API",
        default_version='v1',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url=settings.SWAGGER_BASE_URL

)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0)),
] 