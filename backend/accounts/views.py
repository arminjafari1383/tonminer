from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import create_guest_user


class GuestRateThrottle(AnonRateThrottle):
    scope = "guest"


class GuestView(APIView):
    """Creates an account with a random ID and returns JWT tokens. No login/signup."""
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [GuestRateThrottle]

    def post(self, request):
        user = create_guest_user(request.data.get("referral_code", ""))
        refresh = RefreshToken.for_user(user)
        return Response(
            {"id": user.id, "username": user.username,
             "access": str(refresh.access_token), "refresh": str(refresh)},
            status=201,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username})
