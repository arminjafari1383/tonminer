from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

class MiningPlan(models.Model):
    class Tier(models.TextChoices):
        BRONZE = 'bronze', 'Bronze'
        SILVER = 'silver', 'Silver'
        GOLD = 'gold', 'Gold'
    name = models.CharField(max_length=80)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.BRONZE)
    amount_ton = models.DecimalField(max_digits=18, decimal_places=4, validators=[MinValueValidator(3)])
    daily_rate_percent = models.DecimalField(max_digits=6, decimal_places=3, validators=[MinValueValidator(0)])
    active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['sort_order', 'amount_ton']
    def __str__(self): return f'{self.name} ({self.amount_ton} TON)'

class MinerAccount(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='miner_account')
    wallet_address = models.CharField(max_length=80, blank=True)
    balance_ton = models.DecimalField(max_digits=24, decimal_places=8, default=0)
    deposit_total_ton = models.DecimalField(max_digits=24, decimal_places=8, default=0)
    deposit_earned_ton = models.DecimalField(max_digits=24, decimal_places=8, default=0)
    mining_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f'Miner account: {self.user}'

class Deposit(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        REJECTED = 'rejected', 'Rejected'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='miner_deposits')
    plan = models.ForeignKey(MiningPlan, on_delete=models.PROTECT, related_name='deposits', null=True, blank=True)
    amount_ton = models.DecimalField(max_digits=24, decimal_places=8, validators=[MinValueValidator(3)])
    transaction_hash = models.CharField(max_length=128, blank=True, db_index=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f'{self.amount_ton} TON · {self.user} · {self.status}'

class WithdrawalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        APPROVED = 'approved', 'Approved'
        PAID = 'paid', 'Paid'
        REJECTED = 'rejected', 'Rejected'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='miner_withdrawals')
    amount_ton = models.DecimalField(max_digits=24, decimal_places=8, validators=[MinValueValidator(100)])
    destination_wallet = models.CharField(max_length=80)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    admin_note = models.TextField(blank=True)
    transaction_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return f'Withdrawal {self.amount_ton} TON · {self.user}'

class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='referrals_sent')
    referred_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='referred_by')
    reward_ton = models.DecimalField(max_digits=18, decimal_places=8, default=1)
    reward_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f'{self.referrer} → {self.referred_user}'

class SiteSetting(models.Model):
    key = models.SlugField(unique=True)
    value = models.CharField(max_length=500)
    description = models.CharField(max_length=250, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.key
