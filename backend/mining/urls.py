from django.urls import path
from .views import DashboardView, WalletView
urlpatterns = [path("mining/dashboard/", DashboardView.as_view()), path("wallet/", WalletView.as_view())]
