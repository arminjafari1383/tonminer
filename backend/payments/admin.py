from django.contrib import admin
from .models import PaymentOrder

@admin.register(PaymentOrder)
class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ("id","user","amount","status","wallet","transaction_hash","created_at")
    list_filter = ("status","created_at")
    search_fields = ("id","user__username","wallet","memo","transaction_hash")
    readonly_fields = ("id","memo","created_at","confirmed_at","transaction_hash")
