from django.urls import path
from .views import ReferralView
urlpatterns = [path("referrals/", ReferralView.as_view())]
