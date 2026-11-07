from django.conf import settings
from django.db import models
class MiningAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mining_account")
    balance = models.DecimalField(max_digits=30, decimal_places=16, default=0)
    deposit_yield_earned = models.DecimalField(max_digits=30, decimal_places=16, default=0)
    free_cycle_started_at = models.DateTimeField(auto_now_add=True)
    last_accrued_at = models.DateTimeField(auto_now_add=True)
    wallet_address = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Deposit(models.Model):
    STATUS = [("pending","Pending"),("confirmed","Confirmed"),("rejected","Rejected")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deposits")
    amount = models.DecimalField(max_digits=24, decimal_places=9)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    chain_tx_hash = models.CharField(max_length=128, blank=True, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

class MiningPosition(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mining_positions")
    deposit = models.OneToOneField(Deposit, on_delete=models.PROTECT)
    principal = models.DecimalField(max_digits=24, decimal_places=9)
    daily_rate_percent = models.DecimalField(max_digits=8, decimal_places=4)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
