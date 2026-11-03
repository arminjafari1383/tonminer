import json,re,secrets,time,logging
from decimal import Decimal,InvalidOperation
from datetime import timedelta
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_GET,require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import requests
from .models import Payment

log=logging.getLogger(__name__)

ADDRESS_RE=re.compile(r'^(?:EQ|UQ|kQ|0Q)[A-Za-z0-9_-]{46}$')

def result(p):
 return {'id':str(p.id),'status':p.status,'amount':str(Decimal(p.amount_nano)/Decimal(10**9)),'memo':p.memo,'receiver':settings.TON_RECEIVER,'tx_hash':p.tx_hash}

@csrf_exempt
@require_POST
def create_payment(request):
 if not settings.TON_RECEIVER or not ADDRESS_RE.fullmatch(settings.TON_RECEIVER):
  return JsonResponse({'error':'TON_RECEIVER is not configured with a valid wallet address'},status=503)
 if settings.TON_NETWORK!='mainnet':
  return JsonResponse({'error':'This configuration only supports mainnet'},status=503)
 try:
  body=json.loads(request.body)
  wallet=str(body.get('wallet','')).strip()
  amount=Decimal(str(body.get('amount','')))
  nano=amount*Decimal(10**9)
  if not ADDRESS_RE.fullmatch(wallet) or not amount.is_finite() or nano!=nano.to_integral_value() or not (Decimal('1')<=amount<=Decimal('100000')):
   raise ValueError()
 except (ValueError,InvalidOperation,TypeError,KeyError,json.JSONDecodeError):
  return JsonResponse({'error':'Invalid wallet or amount (minimum 1 TON)'},status=400)
 p=Payment.objects.create(wallet=wallet,amount_nano=int(nano),memo='TONMINER-'+secrets.token_hex(12))
 return JsonResponse(result(p),status=201)

def find_transfer(p):
 key=(settings.TONCENTER_API_KEY or '').strip()
 # Ignore empty/placeholder keys: a bad key makes Toncenter reject every request.
 headers={'X-API-Key':key} if key and not key.upper().startswith('YOUR_') else {}
 url=settings.TONCENTER_URL.rstrip('/')+'/getTransactions'
 params={'address':settings.TON_RECEIVER,'limit':100,'archival':'true'}
 for attempt in range(3):
  response=requests.get(url,params=params,headers=headers,timeout=15)
  if response.status_code==429 and attempt<2:
   time.sleep(1.5);continue  # free tier without key: ~1 request/second
  break
 if response.status_code>=400:
  log.warning('Toncenter HTTP %s: %s',response.status_code,response.text[:300])
 response.raise_for_status()
 data=response.json()
 if not data.get('ok'): raise ValueError('TON API unavailable')
 for tx in data.get('result',[]):
  incoming=tx.get('in_msg') or {}
  # Toncenter v2 message contains decoded text comment when applicable.
  if (incoming.get('message') or '').strip()!=p.memo:continue
  if int(incoming.get('value') or 0)!=p.amount_nano:continue
  source=incoming.get('source') or ''
  # Compare addresses canonically (Toncenter can return different friendly formats).
  if not same_address(source,p.wallet):continue
  if tx.get('description',{}).get('aborted') is True:continue
  if tx.get('transaction_id',{}).get('hash'):
   return tx['transaction_id']['hash']
 return None

def same_address(a,b):
 # TON friendly addresses share the same 32-byte account ID even if bounce flags differ.
 import base64
 def decode(x):
  if ':' in x:return x.lower()
  try:
   raw=base64.urlsafe_b64decode(x+'==')
   if len(raw)!=36:return None
   return f'{int.from_bytes(raw[1:2],"big",signed=True)}:{raw[2:34].hex()}'
  except Exception:return None
 return decode(a) is not None and decode(a)==decode(b)

@require_GET
def payment_status(request,payment_id):
 try:p=Payment.objects.get(pk=payment_id)
 except Payment.DoesNotExist:return JsonResponse({'error':'Not found'},status=404)
 if p.status=='pending':
  if p.created_at<timezone.now()-timedelta(hours=24):
   p.status='expired';p.save(update_fields=['status'])
  else:
   try:
    tx_hash=find_transfer(p)
    if tx_hash:
     with transaction.atomic():
      p=Payment.objects.select_for_update().get(pk=p.pk)
      if p.status=='pending' and not Payment.objects.filter(tx_hash=tx_hash).exclude(pk=p.pk).exists():
       p.status='confirmed';p.tx_hash=tx_hash;p.confirmed_at=timezone.now();p.save(update_fields=['status','tx_hash','confirmed_at'])
   except (requests.RequestException,ValueError,TypeError) as exc:
    log.warning('Payment lookup failed for %s: %r',p.id,exc)
    return JsonResponse({**result(p),'verification_error':'Blockchain lookup temporarily unavailable'},status=503)
 return JsonResponse(result(p))
