"""
TreasuryMind AI - Transaction Views & Serializers
"""

from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters import rest_framework as django_filters

from .models import Transaction, TransactionType, TransactionStatus
from apps.agents.tasks import run_cashflow_agent


# ─── Serializers ──────────────────────────────────────────────────────────────
from rest_framework import serializers


class TransactionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'reference_number']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        transaction = super().create(validated_data)
        # Trigger async agent pipeline after new transaction
        run_cashflow_agent.delay(str(transaction.id))
        return transaction


# ─── Filters ──────────────────────────────────────────────────────────────────
class TransactionFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='transaction_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='transaction_date', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'category', 'status', 'currency', 'date_from', 'date_to']


# ─── Views ────────────────────────────────────────────────────────────────────
class TransactionListView(generics.ListCreateAPIView):
    queryset = Transaction.objects.select_related('created_by').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = TransactionFilter
    search_fields = ['title', 'description', 'counterparty', 'reference_number']
    ordering_fields = ['amount', 'transaction_date', 'created_at']
    ordering = ['-transaction_date']


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def transaction_summary(request):
    """Aggregate summary of transactions for dashboard widgets."""
    period = request.query_params.get('period', '30')  # days
    try:
        days = int(period)
    except ValueError:
        days = 30

    since = timezone.now().date() - timezone.timedelta(days=days)
    qs = Transaction.objects.filter(
        transaction_date__gte=since,
        status=TransactionStatus.COMPLETED
    )

    total_inflow = qs.filter(transaction_type=TransactionType.INFLOW).aggregate(
        total=Sum('amount'))['total'] or 0
    total_outflow = qs.filter(transaction_type=TransactionType.OUTFLOW).aggregate(
        total=Sum('amount'))['total'] or 0

    net_cashflow = total_inflow - total_outflow
    liquidity_score = min(100, max(0, int((float(net_cashflow) / max(float(total_outflow), 1)) * 100 + 50)))

    # Category breakdown
    category_breakdown = list(
        qs.values('category', 'transaction_type')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )

    # Daily trend (last N days)
    from django.db.models.functions import TruncDate
    daily_trend = list(
        qs.annotate(date=TruncDate('transaction_date'))
        .values('date', 'transaction_type')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    return Response({
        'period_days': days,
        'total_inflow': float(total_inflow),
        'total_outflow': float(total_outflow),
        'net_cashflow': float(net_cashflow),
        'liquidity_score': liquidity_score,
        'transaction_count': qs.count(),
        'category_breakdown': category_breakdown,
        'daily_trend': daily_trend,
    })
