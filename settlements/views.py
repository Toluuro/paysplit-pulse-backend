# settlements/views.py
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SplitRequestSerializer
from .models import Transaction, PayoutLedger
from .tasks import async_process_split
from rest_framework import generics
from django.db.models import Sum, Count
from .serializers import TransactionSerializer

class WebhookSettlementAPIView(APIView):
    """
    Simulates receiving a webhook from a bank or payment gateway.
    It queues the transaction for background processing and immediately responds with a 202 Accepted.
    """
    def post(self, request):
        serializer = SplitRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            
            # 1. Register the raw transaction as PENDING
            txn, created = Transaction.objects.get_or_create(
                transaction_id=data['transaction_id'],
                defaults={'amount': data['amount'], 'status': 'PENDING'}
            )
            
            if not created:
                return Response(
                    {"error": "Transaction ID already exists. Duplicate webhook prevented."}, 
                    status=status.HTTP_409_CONFLICT
                )

            # 2. Fire the Celery Task (Async Dispatch)
            async_process_split.delay(
                txn.id, 
                data['rule_id'], 
                data['primary_vendor_id'], 
                data.get('agent_id')
            )

            # 3. Respond to the payment gateway instantly
            return Response({
                "message": "Transaction accepted and queued for settlement processing.",
                "transaction_id": txn.transaction_id,
                "status": "PROCESSING_QUEUED"
            }, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Add these classes to the bottom of the file
# Replace your existing GET views with these locked-down versions:
class TransactionListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] # <-- Locks down the endpoint
    serializer_class = TransactionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            # Admins see everything
            return Transaction.objects.prefetch_related('payouts').order_by('-created_at')
        else:
            # Agents ONLY see transactions where they received an agent commission
            return Transaction.objects.filter(payouts__recipient_type='AGENT_COMMISSION').distinct().order_by('-created_at')

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated] # <-- Locks down the endpoint

    def get(self, request):
        user = request.user
        
        if user.is_superuser:
            # ADMIN VIEW: Master Ledger Stats
            processed_txns = Transaction.objects.filter(status='PROCESSED')
            total_volume = processed_txns.aggregate(Sum('amount'))['amount__sum'] or 0.00
            status_counts = Transaction.objects.values('status').annotate(count=Count('status'))
            
            stats = {
                "role": "admin",
                "total_volume": total_volume,
                "metrics": {item['status']: item['count'] for item in status_counts}
            }
        else:
            # AGENT VIEW: Personal Wallet Stats
            agent_payouts = PayoutLedger.objects.filter(recipient_type='AGENT_COMMISSION')
            total_earnings = agent_payouts.aggregate(Sum('amount'))['amount__sum'] or 0.00
            
            stats = {
                "role": "agent",
                "total_volume": total_earnings,
                "metrics": {"YOUR PAYOUTS": agent_payouts.count()}
            }
            
        return Response(stats, status=status.HTTP_200_OK)