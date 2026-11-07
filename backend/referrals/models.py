import secrets
from django.conf import settings
from django.db import models

def make_referral_code():
    return secrets.token_urlsafe(8).replace("-", "").replace("_", "")[:10].upper()

class ReferralProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referral_profile")
    code = models.CharField(max_length=16, unique=True, default=make_referral_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.code})"

class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referrals")
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="referred_by")
    reward_amount = models.DecimalField(max_digits=18, decimal_places=9, default=1)
    verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer} -> {self.referred_user}"
