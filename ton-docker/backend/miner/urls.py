from django.urls import path
from .views import HealthView, PlanListView, MyAccountView, MyDepositListCreateView, MyWithdrawalListCreateView
urlpatterns = [path('health/', HealthView.as_view(), name='health'), path('plans/', PlanListView.as_view(), name='plans'), path('me/', MyAccountView.as_view(), name='my-account'), path('deposits/', MyDepositListCreateView.as_view(), name='deposits'), path('withdrawals/', MyWithdrawalListCreateView.as_view(), name='withdrawals')]
