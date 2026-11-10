import secrets
from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings
from django.db import IntegrityError, transaction
from referrals.models import Referral, ReferralProfile
from mining.models import MiningAccount

REFERRAL_REWARD_TON = Decimal("1.000000000")


def _random_username():
    return "u_" + secrets.token_hex(8)


@transaction.atomic
def create_guest_user(referral_code=""):
    """Create a user with a random ID (no email/password) plus its related rows."""
    referral_code = (referral_code or "").strip().upper()
    referrer = None
    if referral_code:
        profile = (
            ReferralProfile.objects.select_for_update()
            .filter(code__iexact=referral_code)
            .select_related("user")
            .first()
        )
        referrer = profile.user if profile else None  # invalid code is ignored

    user = None
    for _ in range(5):
        try:
            with transaction.atomic():
                user = User.objects.create_user(username=_random_username(), password=None)
            break
        except IntegrityError:
            continue
    if user is None:
        raise RuntimeError("Could not generate a unique user id")

    ReferralProfile.objects.create(user=user)
    MiningAccount.objects.get_or_create(user=user)

    if referrer and referrer.pk != user.pk:
        Referral.objects.create(
            referrer=referrer,
            referred_user=user,
            reward_amount=REFERRAL_REWARD_TON if settings.DEMO_MODE else Decimal("0"),
            verified=True,
        )
        if settings.DEMO_MODE:
            acc, _ = MiningAccount.objects.select_for_update().get_or_create(user=referrer)
            acc.balance += REFERRAL_REWARD_TON
            acc.save(update_fields=["balance"])

    return user
