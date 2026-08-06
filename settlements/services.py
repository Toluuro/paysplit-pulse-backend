# settlements/services.py
from decimal import Decimal, ROUND_DOWN
from django.db import transaction as db_transaction
from .models import PayoutLedger

def process_transaction_split(transaction_record, split_rule, primary_vendor, agent_vendor=None):
    """
    Executes the financial split mathematically without floating-point rounding errors.
    """
    total_amount = transaction_record.amount
    
    # 1. Calculate strict cuts using ROUND_DOWN to prevent artificial money creation
    # We divide by Decimal('100') to convert the percentage (e.g., 10.00) to a decimal (0.10)
    platform_amount = (total_amount * (split_rule.platform_cut / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    agent_amount = (total_amount * (split_rule.agent_cut / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    vendor_amount = (total_amount * (split_rule.vendor_cut / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    
    # 2. The Orphan Penny Problem
    # Due to rounding down, a $10.00 split three ways ($3.33 each) leaves $0.01 unallocated.
    calculated_total = platform_amount + agent_amount + vendor_amount
    remainder = total_amount - calculated_total
    
    # We allocate the leftover remainder to the platform fee to ensure the ledger balances perfectly
    platform_amount += remainder

    # 3. Database Transaction (All or Nothing)
    # If the database crashes mid-save, db_transaction.atomic() rolls back everything 
    # so we don't accidentally pay the vendor but forget to charge the platform fee.
    with db_transaction.atomic():
        
        # Create Platform Fee Ledger
        PayoutLedger.objects.create(
            transaction=transaction_record,
            vendor=None, # Platform funds stay in-house
            recipient_type='PLATFORM_FEE',
            amount=platform_amount
        )
        
        # Create Agent Commission Ledger (if applicable)
        if agent_vendor and agent_amount > 0:
            PayoutLedger.objects.create(
                transaction=transaction_record,
                vendor=agent_vendor,
                recipient_type='AGENT_COMMISSION',
                amount=agent_amount
            )
            
        # Create Primary Vendor Ledger
        PayoutLedger.objects.create(
            transaction=transaction_record,
            vendor=primary_vendor,
            recipient_type='VENDOR_PAYOUT',
            amount=vendor_amount
        )
        
        # Lock the transaction as successfully processed
        transaction_record.status = 'PROCESSED'
        transaction_record.save()
        
    return True