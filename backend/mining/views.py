from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import dashboard_for, accrue
from .models import MiningAccount
from payments.tonchain import normalize_ton_address
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(dashboard_for(request.user))
class WalletView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        address = str(request.data.get("wallet_address","")).strip()
        try:
            # Validate checksum and canonicalize before binding the wallet to this account.
            address = normalize_ton_address(address)
        except (TypeError, ValueError):
            return Response({"detail":"Invalid TON wallet address."}, status=400)
        account, _ = MiningAccount.objects.get_or_create(user=request.user)
        account.wallet_address = address
        account.save(update_fields=["wallet_address"])
        return Response({"wallet_address":account.wallet_address})
