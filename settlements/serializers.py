# settlements/serializers.py
from rest_framework import serializers

class SplitRequestSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    rule_id = serializers.IntegerField()
    primary_vendor_id = serializers.IntegerField()
    agent_id = serializers.IntegerField(required=False, allow_null=True)

# Add to the bottom of settlements/serializers.py
from .models import Transaction, PayoutLedger

class PayoutLedgerSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = PayoutLedger
        fields = ['id', 'recipient_type', 'vendor_name', 'amount', 'is_dispatched', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    payouts = PayoutLedgerSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'transaction_id', 'amount', 'status', 'created_at', 'payouts']