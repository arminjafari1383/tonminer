from django.urls import path
from .views import WithdrawalView
urlpatterns = [path("", WithdrawalView.as_view())]
