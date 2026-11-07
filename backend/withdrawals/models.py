from django.conf import settings
from django.db import models
class Withdrawal(models.Model):
    STATUS = [("pending","Pending"),("approved","Approved"),("paid","Paid"),("rejected","Rejected")]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=24, decimal_places=9)
    wallet_address = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    tx_hash = models.CharField(max_length=128, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
