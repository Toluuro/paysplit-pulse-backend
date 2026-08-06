from django.db import models
from decimal import Decimal

class Vendor(models.Model):
    """The entities receiving funds (e.g., Real Estate Agent, Property Developer)"""
    name = models.CharField(max_length=255)
    bank_account_number = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SplitRule(models.Model):
    """The blueprint for how funds should be divided"""
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Standard PropTech Split")
    platform_cut = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (e.g., 10.00)")
    agent_cut = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (e.g., 20.00)")
    vendor_cut = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage (e.g., 70.00)")
    
    def __str__(self):
        return self.name

class Transaction(models.Model):
    """The raw inbound payment that needs to be split"""
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2) # Handles up to $9.99 Billion
    status = models.CharField(max_length=20, default='PENDING') # PENDING, PROCESSED, FAILED
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - ${self.amount}"

class PayoutLedger(models.Model):
    """The finalized, calculated cuts ready for bank dispatch"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payouts')
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    
    # E.g., 'PLATFORM_FEE', 'AGENT_COMMISSION', 'VENDOR_PAYOUT'
    recipient_type = models.CharField(max_length=50) 
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_dispatched = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient_type} - ${self.amount}"