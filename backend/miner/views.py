from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MiningPlan, MinerAccount, Deposit, WithdrawalRequest
from .serializers import MiningPlanSerializer, MinerAccountSerializer, DepositSerializer, WithdrawalSerializer
class HealthView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request): return Response({'service':'TON Miner API','status':'ok','note':'Payment and chain verification are not configured.'})
class PlanListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = MiningPlanSerializer
    queryset = MiningPlan.objects.filter(active=True)
class MyAccountView(generics.RetrieveAPIView):
    serializer_class = MinerAccountSerializer
    def get_object(self):
        account, _ = MinerAccount.objects.get_or_create(user=self.request.user)
        return account
class MyDepositListCreateView(generics.ListCreateAPIView):
    serializer_class = DepositSerializer
    def get_queryset(self): return Deposit.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        # Intentional: creates a PENDING request only. A trusted chain watcher must confirm it.
        serializer.save(user=self.request.user)
class MyWithdrawalListCreateView(generics.ListCreateAPIView):
    serializer_class = WithdrawalSerializer
    def get_queryset(self): return WithdrawalRequest.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        # Intentional: creates a request only. Do not debit/send funds until policy checks and approval run.
        serializer.save(user=self.request.user)
