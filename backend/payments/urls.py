from django.urls import path
from . import views
urlpatterns=[path('balance/',views.wallet_balance),path('payments/',views.create_payment),path('payments/<uuid:payment_id>/',views.payment_status)]
