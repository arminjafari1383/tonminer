import uuid
from django.db import models
class Payment(models.Model):
 id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
 wallet=models.CharField(max_length=128)
 amount_nano=models.BigIntegerField()
 memo=models.CharField(max_length=96,unique=True)
 status=models.CharField(max_length=12,default='pending',choices=[('pending','Pending'),('confirmed','Confirmed'),('expired','Expired')])
 tx_hash=models.CharField(max_length=128,null=True,blank=True,unique=True)
 created_at=models.DateTimeField(auto_now_add=True)
 confirmed_at=models.DateTimeField(null=True,blank=True)
 @property
 def amount_ton(self): return self.amount_nano/10**9


class CreditLedger(models.Model):
    """One immutable credit per verified on-chain payment."""
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name='credit')
    wallet_key = models.CharField(max_length=80, db_index=True)
    amount_nano = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
