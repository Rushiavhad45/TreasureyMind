from celery import shared_task
import logging
logger = logging.getLogger('apps')

@shared_task
def refresh_cashflow_metrics():
    """Refresh cash flow snapshot for today."""
    from django.utils import timezone
    from django.db.models import Sum
    from apps.transactions.models import Transaction, TransactionType, TransactionStatus
    from apps.cashflow.models import CashFlowSnapshot
    
    today = timezone.now().date()
    thirty_ago = today - timezone.timedelta(days=30)
    
    inflow = Transaction.objects.filter(
        transaction_type=TransactionType.INFLOW,
        status=TransactionStatus.COMPLETED,
        transaction_date__gte=thirty_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    outflow = Transaction.objects.filter(
        transaction_type=TransactionType.OUTFLOW,
        status=TransactionStatus.COMPLETED,
        transaction_date__gte=thirty_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net = inflow - outflow
    score = min(100, max(0, int((float(net) / max(float(outflow), 1)) * 100 + 50)))
    
    CashFlowSnapshot.objects.update_or_create(
        snapshot_date=today,
        defaults={'total_inflow': inflow, 'total_outflow': outflow, 'net_cashflow': net, 'liquidity_score': score}
    )
    logger.info(f"CashFlow snapshot refreshed for {today}")
