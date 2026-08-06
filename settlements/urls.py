# settlements/urls.py
from django.urls import path
from .views import WebhookSettlementAPIView, TransactionListAPIView, DashboardStatsAPIView

urlpatterns = [
    path('api/webhooks/settle/', WebhookSettlementAPIView.as_view(), name='webhook-settle'),
    
    # New GET endpoints for the Next.js Frontend
    path('api/transactions/', TransactionListAPIView.as_view(), name='transaction-list'),
    path('api/dashboard/stats/', DashboardStatsAPIView.as_view(), name='dashboard-stats'),
]