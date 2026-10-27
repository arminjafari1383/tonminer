from rest_framework import serializers
from .models import MiningPlan, MinerAccount, Deposit, WithdrawalRequest
class MiningPlanSerializer(serializers.ModelSerializer):
    class Meta: model = MiningPlan; fields = ['id','name','tier','amount_ton','daily_rate_percent','active','sort_order']
class MinerAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta: model = MinerAccount; fields = ['id','username','wallet_address','balance_ton','deposit_total_ton','deposit_earned_ton','mining_enabled','created_at','updated_at']; read_only_fields = ['balance_ton','deposit_total_ton','deposit_earned_ton','created_at','updated_at']
class DepositSerializer(serializers.ModelSerializer):
    class Meta: model = Deposit; fields = ['id','plan','amount_ton','transaction_hash','status','created_at','confirmed_at']; read_only_fields = ['status','created_at','confirmed_at']
class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta: model = WithdrawalRequest; fields = ['id','amount_ton','destination_wallet','status','admin_note','transaction_hash','created_at','processed_at']; read_only_fields = ['status','admin_note','transaction_hash','created_at','processed_at']
    def validate_destination_wallet(self, value):
        if not value.startswith(('UQ','EQ')) or len(value) != 48: raise serializers.ValidationError('Enter a valid TON wallet address.')
        return value
    def validate_amount_ton(self, value):
        if value < 100: raise serializers.ValidationError('Minimum withdrawal is 100 TON.')
        return value
