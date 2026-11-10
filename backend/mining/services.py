from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import MiningAccount, MiningPosition
from .constants import FREE_CYCLE_SECONDS, FREE_CYCLE_REWARD_TON, DEPOSIT_YIELD_CAP_MULTIPLIER, MIN_WITHDRAW_TON

D = Decimal
@transaction.atomic
def accrue(user):
    account, _ = MiningAccount.objects.select_for_update().get_or_create(user=user)
    from django.conf import settings
    now = timezone.now()
    if not settings.DEMO_MODE:
        # No synthetic mining, free-cycle or yield rewards in live-payment mode.
        account.last_accrued_at = now
        account.save(update_fields=["last_accrued_at"])
        return account
    elapsed = max(0, (now - account.last_accrued_at).total_seconds())
    if elapsed <= 0:
        return account
    positions = list(MiningPosition.objects.select_for_update().filter(user=user, active=True))
    principal = sum((p.principal for p in positions), D("0"))
    daily_yield = sum((p.principal * p.daily_rate_percent / D("100") for p in positions), D("0"))
    wanted = daily_yield * D(str(elapsed)) / D("86400")
    cap = principal * D(DEPOSIT_YIELD_CAP_MULTIPLIER)
    room = max(D("0"), cap - account.deposit_yield_earned)
    deposit_reward = min(wanted, room)
    account.deposit_yield_earned += deposit_reward
    account.balance += deposit_reward

    cycle_elapsed = max(0, (now - account.free_cycle_started_at).total_seconds())
    cycles = int(cycle_elapsed // FREE_CYCLE_SECONDS)
    if cycles:
        account.balance += D(FREE_CYCLE_REWARD_TON) * cycles
        account.free_cycle_started_at += timedelta(seconds=FREE_CYCLE_SECONDS * cycles)
    account.last_accrued_at = now
    account.save()
    return account

def dashboard_for(user):
    from django.conf import settings
    from django.db.models import Sum
    from referrals.models import Referral
    MiningAccount.objects.get_or_create(user=user)
    account = accrue(user)
    positions = list(MiningPosition.objects.filter(user=user, active=True))
    principal = sum((p.principal for p in positions), D("0"))
    daily = sum((p.principal * p.daily_rate_percent / D("100") for p in positions), D("0"))
    next_cycle = account.free_cycle_started_at + timedelta(seconds=FREE_CYCLE_SECONDS)

    # Lifetime earnings by source (no extra DB column needed)
    if settings.DEMO_MODE:
        cycles_done = int(round((account.free_cycle_started_at - account.created_at).total_seconds() / FREE_CYCLE_SECONDS))
        free_earned = D(FREE_CYCLE_REWARD_TON) * max(0, cycles_done)
        referral_earned = Referral.objects.filter(referrer=user).aggregate(t=Sum("reward_amount"))["t"] or D("0")
    else:
        free_earned = D("0")
        referral_earned = D("0")
    yield_earned = account.deposit_yield_earned
    total_mined = free_earned + referral_earned + yield_earned
    return {
        "demo": settings.DEMO_MODE,
        "total_mined": str(total_mined),
        "free_earned": str(free_earned),
        "referral_earned": str(referral_earned),
        "yield_earned": str(yield_earned),
        "balance": str(account.balance),
        "wallet_address": account.wallet_address,
        "deposit_total": str(principal),
        "daily_deposit_yield": str(daily),
        "deposit_yield_earned": str(account.deposit_yield_earned),
        "deposit_yield_cap": str(principal * D(DEPOSIT_YIELD_CAP_MULTIPLIER)),
        "min_withdraw": MIN_WITHDRAW_TON,
        "free_th": 10,
        "free_cycle_seconds": FREE_CYCLE_SECONDS,
        "free_cycle_reward": FREE_CYCLE_REWARD_TON,
        "next_free_cycle_at": next_cycle.isoformat(),
        "positions": [{"principal": str(p.principal), "daily_rate_percent": str(p.daily_rate_percent)} for p in positions],
    }
