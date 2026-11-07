from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mining.models import MiningAccount
from mining.services import accrue
from mining.constants import MIN_WITHDRAW_TON
from .models import Withdrawal


def payload(w):
    return {"id": w.id, "amount": str(w.amount), "wallet_address": w.wallet_address,
            "status": w.status, "tx_hash": w.tx_hash, "created_at": w.created_at.isoformat(),
            "simulated": w.tx_hash.startswith("demo-")}


class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Withdrawal.objects.filter(user=request.user).order_by("-created_at")
        return Response([payload(w) for w in qs])

    @transaction.atomic
    def post(self, request):
        MiningAccount.objects.select_for_update().get_or_create(user=request.user)
        account = accrue(request.user)
        try:
            amount = Decimal(str(request.data.get("amount")))
        except Exception:
            return Response({"detail": "Invalid amount."}, status=400)
        if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -9:
            return Response({"detail": "Invalid amount."}, status=400)
        if amount < Decimal(MIN_WITHDRAW_TON):
            return Response({"detail": f"Minimum withdrawal is {MIN_WITHDRAW_TON} TON."}, status=400)
        if amount > account.balance:
            return Response({"detail": "Insufficient balance."}, status=400)

        if settings.DEMO_MODE:
            wallet = str(request.data.get("wallet_address", "")).strip()
            if not 10 <= len(wallet) <= 128:
                return Response({"detail": "Enter a destination wallet address (10-128 characters)."}, status=400)
            account.wallet_address = wallet
        elif not account.wallet_address:
            return Response({"detail": "Connect a wallet first."}, status=400)

        account.balance -= amount
        account.save()
        w = Withdrawal.objects.create(user=request.user, amount=amount, wallet_address=account.wallet_address)
        if settings.DEMO_MODE:
            # Simulation only: nothing is sent on-chain.
            w.status = "paid"
            w.tx_hash = "demo-" + str(w.id)
            w.processed_at = timezone.now()
            w.save(update_fields=["status", "tx_hash", "processed_at"])
        return Response(payload(w), status=201)
