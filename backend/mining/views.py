from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services import dashboard_for, accrue
from .models import MiningAccount
class DashboardView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(dashboard_for(request.user))
class WalletView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        address = str(request.data.get("wallet_address","")).strip()
        # TON raw/user-friendly addresses require proper TON address parsing in production.
        if len(address) < 40 or len(address) > 128:
            return Response({"detail":"Invalid wallet address."}, status=400)
        account, _ = MiningAccount.objects.get_or_create(user=request.user)
        account.wallet_address = address
        account.save(update_fields=["wallet_address"])
        return Response({"wallet_address":account.wallet_address})
