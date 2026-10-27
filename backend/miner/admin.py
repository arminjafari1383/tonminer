from django.contrib import admin
from .models import MiningPlan, MinerAccount, Deposit, WithdrawalRequest, Referral, SiteSetting
admin.site.site_header = 'TON Miner · مرکز مدیریت'
admin.site.site_title = 'TON Miner Admin'
admin.site.index_title = 'مدیریت کاربران، پلن‌ها و عملیات مالی'
@admin.register(MiningPlan)
class MiningPlanAdmin(admin.ModelAdmin):
    list_display = ('name','tier','amount_ton','daily_rate_percent','active','sort_order')
    list_filter = ('tier','active'); search_fields = ('name',); list_editable = ('active','sort_order','daily_rate_percent'); ordering = ('sort_order','amount_ton')
@admin.register(MinerAccount)
class MinerAccountAdmin(admin.ModelAdmin):
    list_display = ('user','wallet_address','balance_ton','deposit_total_ton','mining_enabled','updated_at')
    search_fields = ('user__username','user__email','wallet_address'); list_filter = ('mining_enabled',); readonly_fields = ('created_at','updated_at')
@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user','amount_ton','status','transaction_hash','created_at','confirmed_at')
    list_filter = ('status','created_at'); search_fields = ('user__username','transaction_hash'); readonly_fields = ('created_at',); list_per_page = 50
@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user','amount_ton','destination_wallet','status','created_at','processed_at')
    list_filter = ('status','created_at'); search_fields = ('user__username','destination_wallet','transaction_hash'); list_editable = ('status',); readonly_fields = ('created_at',); list_per_page = 50
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer','referred_user','reward_ton','reward_paid','created_at'); list_filter = ('reward_paid','created_at'); search_fields = ('referrer__username','referred_user__username')
@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key','value','description','updated_at'); search_fields = ('key','description')
