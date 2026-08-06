# settlements/admin.py
from django.contrib import admin
from .models import Vendor, SplitRule, Transaction, PayoutLedger

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'bank_account_number', 'is_active')

@admin.register(SplitRule)
class SplitRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'platform_cut', 'agent_cut', 'vendor_cut')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'amount', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(PayoutLedger)
class PayoutLedgerAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'recipient_type', 'vendor', 'amount', 'is_dispatched')
    list_filter = ('recipient_type', 'is_dispatched')