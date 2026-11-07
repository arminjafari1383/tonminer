import uuid
from django.conf import settings
from django.db import models

class PaymentOrder(models.Model):
    STATUS = [("pending","Pending"),("confirmed","Confirmed"),("expired","Expired")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ton_payment_orders")
    wallet = models.CharField(max_length=128)
    receiver = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=24, decimal_places=9)
    memo = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    transaction_hash = models.CharField(max_length=128, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.id} · {self.amount} TON · {self.status}"
