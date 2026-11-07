import secrets
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from mining.models import MiningAccount, Deposit
from .models import PaymentOrder
from .tonchain import normalize_ton_address, find_matching_payment

MIN_AMOUNT = Decimal("1")
MAX_AMOUNT = Decimal("100000")
ORDER_TTL = timedelta(minutes=15)

def order_payload(order):
    return {
        "id": str(order.id),
        "wallet": order.wallet,
        "receiver": order.receiver,
        "amount": str(order.amount),
        "memo": order.memo,
        "status": order.status,
        "transaction_hash": order.transaction_hash,
        "created_at": order.created_at.isoformat(),
        "confirmed_at": order.confirmed_at.isoformat() if order.confirmed_at else None,
    }

class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            amount = Decimal(str(request.data.get("amount", "")))
            wallet = str(request.data.get("wallet", "")).strip()
            normalize_ton_address(wallet)
        except (InvalidOperation, ValueError):
            return Response({"error":"مبلغ یا آدرس کیف پول معتبر نیست."}, status=status.HTTP_400_BAD_REQUEST)

        if not amount.is_finite() or amount < MIN_AMOUNT or amount > MAX_AMOUNT:
            return Response({"error":"مبلغ معتبر حداقل ۱ و حداکثر ۱۰۰۰۰۰ TON است."}, status=400)
        if amount.as_tuple().exponent < -9:
            return Response({"error":"حداکثر ۹ رقم اعشار برای TON مجاز است."}, status=400)

        receiver = getattr(settings, "TON_RECEIVER_ADDRESS", "").strip()
        if not receiver:
            return Response({"error":"آدرس دریافت TON در سرور تنظیم نشده است."}, status=503)
        try:
            normalize_ton_address(receiver)
        except ValueError:
            return Response({"error":"آدرس دریافت TON در تنظیمات سرور معتبر نیست."}, status=503)

        memo = "TM-" + secrets.token_hex(12).upper()
        order = PaymentOrder.objects.create(
            user=request.user,
            wallet=wallet,
            receiver=receiver,
            amount=amount,
            memo=memo,
            expires_at=timezone.now() + ORDER_TTL,
        )
        return Response(order_payload(order), status=status.HTTP_201_CREATED)

class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = PaymentOrder.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({"error":"سفارش پرداخت پیدا نشد."}, status=404)

        if order.status == "pending" and timezone.now() >= order.expires_at:
            order.status = "expired"
            order.save(update_fields=["status"])
            return Response(order_payload(order))

        if order.status == "pending":
            try:
                tx_hash = find_matching_payment(order)
            except Exception as exc:
                return Response({"error":"خطا در بررسی شبکه TON؛ دوباره تلاش کنید.", "verification_error":str(exc)}, status=502)

            if tx_hash:
                try:
                    with transaction.atomic():
                        locked = PaymentOrder.objects.select_for_update().get(id=order.id, user=request.user)
                        if locked.status == "pending":
                            # A chain transaction can only settle one order.
                            locked.transaction_hash = tx_hash
                            locked.status = "confirmed"
                            locked.confirmed_at = timezone.now()
                            locked.save(update_fields=["transaction_hash","status","confirmed_at"])
                            account, _ = MiningAccount.objects.select_for_update().get_or_create(user=request.user)
                            account.balance += locked.amount
                            account.save(update_fields=["balance"])
                            Deposit.objects.create(
                                user=request.user,
                                amount=locked.amount,
                                status="confirmed",
                                chain_tx_hash=tx_hash,
                                confirmed_at=locked.confirmed_at,
                            )
                        order = locked
                except IntegrityError:
                    return Response({"error":"این تراکنش قبلاً برای سفارش دیگری ثبت شده است."}, status=409)

        return Response(order_payload(order))
