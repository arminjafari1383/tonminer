from django.contrib import admin
from .models import Referral, ReferralProfile

@admin.register(ReferralProfile)
class ReferralProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at")
    search_fields = ("user__username", "code")

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred_user", "reward_amount", "verified", "created_at")
    list_filter = ("verified", "created_at")
    search_fields = ("referrer__username", "referred_user__username")
