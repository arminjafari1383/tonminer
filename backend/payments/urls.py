from django.urls import path
from . import views
urlpatterns=[path('payments/',views.create_payment),path('payments/<uuid:payment_id>/',views.payment_status)]
