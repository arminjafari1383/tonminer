from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status":"ok","service":"ton-miner-api"})

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("mining.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/", include("referrals.urls")),
    path("api/withdrawals/", include("withdrawals.urls")),
]
