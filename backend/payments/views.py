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
from mining.models import MiningAccount, Deposit, MiningPosition
from mining.services import accrue
from mining.constants import MIN_TOPUP_TON, rate_for
from .models import PaymentOrder
from .tonchain import normalize_ton_address, find_matching_payment

MIN_AMOUNT = Decimal(MIN_TOPUP_TON)
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


def settle_order(order, tx_hash):
    """Mark an order confirmed exactly once and apply its effect to the account."""
    with transaction.atomic():
        locked = PaymentOrder.objects.select_for_update().get(id=order.id)
        if locked.status != "pending":
            return locked
        locked.transaction_hash = tx_hash
        locked.status = "confirmed"
        locked.confirmed_at = timezone.now()
        locked.save(update_fields=["transaction_hash", "status", "confirmed_at"])
        deposit = Deposit.objects.create(
            user=locked.user, amount=locked.amount, status="confirmed",
            chain_tx_hash=tx_hash, confirmed_at=locked.confirmed_at,
        )
        if settings.DEMO_MODE:
            # Bring accrual up to now so the new purchase only earns from this moment,
            # then start its daily profit. The purchase itself is not added to the balance.
            accrue(locked.user)
            MiningPosition.objects.create(
                user=locked.user, deposit=deposit, principal=locked.amount,
                daily_rate_percent=rate_for(locked.amount),
            )
        else:
            account, _ = MiningAccount.objects.select_for_update().get_or_create(user=locked.user)
            account.balance += locked.amount
            account.save(update_fields=["balance"])
        return locked


class PaymentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        demo = settings.DEMO_MODE
        try:
            amount = Decimal(str(request.data.get("amount", "")))
            wallet = str(request.data.get("wallet", "")).strip()
            if demo:
                wallet = (wallet or "demo")[:128]
            else:
                normalize_ton_address(wallet)
        except (InvalidOperation, ValueError):
            return Response({"error": "Invalid amount or wallet address."}, status=status.HTTP_400_BAD_REQUEST)

        if not amount.is_finite() or amount < MIN_AMOUNT or amount > MAX_AMOUNT:
            return Response({"error": f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT} TON."}, status=400)
        if amount.as_tuple().exponent < -9:
            return Response({"error": "At most 9 decimal places are allowed."}, status=400)

        receiver = getattr(settings, "TON_RECEIVER_ADDRESS", "").strip()
        if demo:
            receiver = receiver or "DEMO-MODE-NO-REAL-FUNDS"
        else:
            if not receiver:
                return Response({"error": "The TON receiving address is not configured on the server."}, status=503)
            try:
                normalize_ton_address(receiver)
            except ValueError:
                return Response({"error": "The TON receiving address in the server settings is invalid."}, status=503)

        order = PaymentOrder.objects.create(
            user=request.user, wallet=wallet, receiver=receiver, amount=amount,
            memo="TM-" + secrets.token_hex(12).upper(),
            expires_at=timezone.now() + ORDER_TTL,
        )
        if demo:
            order = settle_order(order, "demo-" + str(order.id))
        return Response(order_payload(order), status=status.HTTP_201_CREATED)


class PaymentStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = PaymentOrder.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({"error": "Payment order not found."}, status=404)

        if order.status == "pending" and settings.DEMO_MODE:
            return Response(order_payload(settle_order(order, "demo-" + str(order.id))))

        if order.status == "pending" and timezone.now() >= order.expires_at:
            order.status = "expired"
            order.save(update_fields=["status"])
            return Response(order_payload(order))

        if order.status == "pending":
            try:
                tx_hash = find_matching_payment(order)
            except Exception as exc:
                return Response({"error": "Could not check the TON network; please try again.", "verification_error": str(exc)}, status=502)
            if tx_hash:
                try:
                    order = settle_order(order, tx_hash)  # a chain transaction can settle only one order
                except IntegrityError:
                    return Response({"error": "This transaction is already linked to another order."}, status=409)

        return Response(order_payload(order))
