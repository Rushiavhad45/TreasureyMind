"""TreasuryMind AI - Alerts Tasks & Views"""

from celery import shared_task
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging

from .models import Alert

logger = logging.getLogger('apps')


@shared_task
def check_and_generate_alerts():
    """Periodic task to check thresholds and generate alerts."""
    from agents.orchestrator import RiskAlertAgent
    from apps.transactions.models import Transaction, TransactionType, TransactionStatus
    from django.db.models import Sum
    from django.utils import timezone

    today = timezone.now().date()
    seven_days_ago = today - timezone.timedelta(days=7)
    thirty_days_ago = today - timezone.timedelta(days=30)

    inflow_30 = Transaction.objects.filter(
        transaction_type=TransactionType.INFLOW,
        status=TransactionStatus.COMPLETED,
        transaction_date__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    outflow_30 = Transaction.objects.filter(
        transaction_type=TransactionType.OUTFLOW,
        status=TransactionStatus.COMPLETED,
        transaction_date__gte=thirty_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    outflow_7 = Transaction.objects.filter(
        transaction_type=TransactionType.OUTFLOW,
        status=TransactionStatus.COMPLETED,
        transaction_date__gte=seven_days_ago
    ).aggregate(total=Sum('amount'))['total'] or 0

    agent = RiskAlertAgent()
    agent.execute({
        'cash_balance': float(inflow_30 - outflow_30),
        'total_outflow_7d': float(outflow_7),
        'liquidity_score': 50,
    })


@shared_task
def send_alert_email(alert_id: str):
    """Send email notification for an alert."""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        alert = Alert.objects.get(id=alert_id)
        send_mail(
            subject=f'[TreasuryMind] {alert.severity.upper()}: {alert.title}',
            message=alert.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER or 'treasury@company.com'],
            fail_silently=True,
        )
        alert.email_sent = True
        alert.save(update_fields=['email_sent'])
    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found for email")


# ─── Serializers ──────────────────────────────────────────────────────────────
class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['created_at']


# ─── Views ────────────────────────────────────────────────────────────────────
class AlertListView(generics.ListAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['severity', 'alert_type', 'is_read', 'is_resolved']
    ordering = ['-created_at']


class AlertDetailView(generics.RetrieveUpdateAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def acknowledge_alert(request, pk):
    """Mark an alert as read/acknowledged."""
    try:
        alert = Alert.objects.get(pk=pk)
        alert.is_read = True
        alert.acknowledged_by = request.user
        alert.acknowledged_at = __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
        alert.save()
        return Response({'detail': 'Alert acknowledged'})
    except Alert.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_stats(request):
    """Summary stats for alert dashboard widget."""
    total = Alert.objects.count()
    unread = Alert.objects.filter(is_read=False).count()
    critical = Alert.objects.filter(severity='critical', is_resolved=False).count()
    return Response({'total': total, 'unread': unread, 'critical': critical})
