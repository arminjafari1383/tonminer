from django.urls import path
from .views import PaymentCreateView, PaymentStatusView

urlpatterns = [
    path("", PaymentCreateView.as_view()),
    path("<uuid:order_id>/", PaymentStatusView.as_view()),
]
