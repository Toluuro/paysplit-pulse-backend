# settlements/tasks.py
from celery import shared_task
from .models import Transaction, SplitRule, Vendor
from .services import process_transaction_split

@shared_task
def async_process_split(transaction_id, rule_id, primary_vendor_id, agent_id=None):
    """
    Pulls the database records and runs the financial math in the background.
    """
    transaction = Transaction.objects.get(id=transaction_id)
    rule = SplitRule.objects.get(id=rule_id)
    primary_vendor = Vendor.objects.get(id=primary_vendor_id)
    agent = Vendor.objects.get(id=agent_id) if agent_id else None

    # Call the service layer we built earlier!
    process_transaction_split(transaction, rule, primary_vendor, agent)
    
    return f"Transaction {transaction.transaction_id} processed successfully."