from decimal import Decimal
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mining.models import MiningAccount
from mining.services import accrue
from mining.constants import MIN_WITHDRAW_TON
from .models import Withdrawal
class WithdrawalView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        qs = Withdrawal.objects.filter(user=request.user).order_by("-created_at")
        return Response([{"id":w.id,"amount":str(w.amount),"wallet_address":w.wallet_address,
                          "status":w.status,"tx_hash":w.tx_hash,"created_at":w.created_at.isoformat()} for w in qs])
    @transaction.atomic
    def post(self, request):
        account = MiningAccount.objects.select_for_update().get(user=request.user)
        account = accrue(request.user)
        try: amount = Decimal(str(request.data.get("amount")))
        except Exception: return Response({"detail":"Invalid amount."}, status=400)
        if amount < Decimal(MIN_WITHDRAW_TON):
            return Response({"detail":f"Minimum withdrawal is {MIN_WITHDRAW_TON} TON."}, status=400)
        if amount > account.balance:
            return Response({"detail":"Insufficient balance."}, status=400)
        if not account.wallet_address:
            return Response({"detail":"Connect a wallet first."}, status=400)
        # Reserve funds immediately; actual on-chain payout is an admin-reviewed workflow.
        account.balance -= amount
        account.save(update_fields=["balance"])
        w = Withdrawal.objects.create(user=request.user, amount=amount, wallet_address=account.wallet_address)
        return Response({"id":w.id,"amount":str(w.amount),"status":w.status}, status=201)
