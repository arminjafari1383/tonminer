from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from .models import MiningAccount, MiningPosition
from .constants import FREE_CYCLE_SECONDS, FREE_CYCLE_REWARD_TON, DEPOSIT_YIELD_CAP_MULTIPLIER

D = Decimal
@transaction.atomic
def accrue(user):
    account, _ = MiningAccount.objects.select_for_update().get_or_create(user=user)
    now = timezone.now()
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
    account, _ = MiningAccount.objects.get_or_create(user=user)
    account = accrue(user)
    positions = list(MiningPosition.objects.filter(user=user, active=True))
    principal = sum((p.principal for p in positions), D("0"))
    daily = sum((p.principal * p.daily_rate_percent / D("100") for p in positions), D("0"))
    next_cycle = account.free_cycle_started_at + timedelta(seconds=FREE_CYCLE_SECONDS)
    return {
        "balance": str(account.balance),
        "wallet_address": account.wallet_address,
        "deposit_total": str(principal),
        "daily_deposit_yield": str(daily),
        "deposit_yield_earned": str(account.deposit_yield_earned),
        "deposit_yield_cap": str(principal * D(DEPOSIT_YIELD_CAP_MULTIPLIER)),
        "free_th": 10,
        "next_free_cycle_at": next_cycle.isoformat(),
        "positions": [{"principal":str(p.principal),"daily_rate_percent":str(p.daily_rate_percent),
                       "plan":p.deposit.status} for p in positions],
    }
