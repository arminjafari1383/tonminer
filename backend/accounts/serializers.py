from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers
from referrals.models import Referral, ReferralProfile
from mining.models import MiningAccount
from decimal import Decimal

REFERRAL_REWARD_TON = Decimal("1.000000000")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=10)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=16)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "referral_code")

    @transaction.atomic
    def create(self, validated_data):
        referral_code = validated_data.pop("referral_code", "").strip().upper()
        referrer = None
        if referral_code:
            profile = ReferralProfile.objects.select_for_update().filter(code__iexact=referral_code).select_related("user").first()
            if not profile:
                raise serializers.ValidationError({"referral_code": "کد دعوت معتبر نیست."})
            referrer = profile.user

        user = User.objects.create_user(**validated_data)
        ReferralProfile.objects.create(user=user)
        MiningAccount.objects.get_or_create(user=user)

        if referrer and referrer.pk != user.pk:
            Referral.objects.create(
                referrer=referrer,
                referred_user=user,
                reward_amount=REFERRAL_REWARD_TON,
                verified=True,
            )
            referrer_account, _ = MiningAccount.objects.select_for_update().get_or_create(user=referrer)
            referrer_account.balance += REFERRAL_REWARD_TON
            referrer_account.save(update_fields=["balance"])

        return user
