import os
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Referral, ReferralProfile

class ReferralView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = ReferralProfile.objects.get_or_create(user=request.user)
        qs = Referral.objects.filter(referrer=request.user).select_related("referred_user").order_by("-created_at")
        bot = os.getenv("TELEGRAM_BOT_USERNAME", "").strip().lstrip("@")
        app = os.getenv("TELEGRAM_APP_SHORT_NAME", "").strip().strip("/")
        invite_link = f"https://t.me/{bot}/{app}?startapp=ref_{profile.code}" if bot and app else ""
        total_reward = qs.aggregate(total=Sum("reward_amount"))["total"] or 0
        return Response({
            "referral_code": profile.code,
            "referral_link": invite_link,
            "count": qs.count(),
            "verified_count": qs.filter(verified=True).count(),
            "total_reward": str(total_reward),
            "reward_per_referral": "1.000000000",
            "items": [{
                "username": r.referred_user.username,
                "verified": r.verified,
                "reward_amount": str(r.reward_amount),
                "created_at": r.created_at.isoformat(),
            } for r in qs],
        })
