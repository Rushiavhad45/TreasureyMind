from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from apps.transactions.models import Transaction
from .models import CashFlowSnapshot
from .serializers import CashFlowSnapshotSerializer


class CashFlowSnapshotListView(APIView):
    """List recent cash flow snapshots."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        snapshots = CashFlowSnapshot.objects.order_by("-snapshot_date")[:30]
        serializer = CashFlowSnapshotSerializer(snapshots, many=True)
        return Response({"results": serializer.data})


class CashFlowMetricsView(APIView):
    """
    Real-time cash flow metrics computed from transactions.
    Returns 30-day rolling metrics used by Dashboard and CashFlowAgent.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now().date()
        days = int(request.query_params.get("days", 30))
        start = now - timedelta(days=days)

        qs = Transaction.objects.filter(
            transaction_date__gte=start,
            status="completed",
        )

        total_inflow = qs.filter(transaction_type="inflow").aggregate(
            s=Sum("amount")
        )["s"] or 0

        total_outflow = qs.filter(transaction_type="outflow").aggregate(
            s=Sum("amount")
        )["s"] or 0

        net = float(total_inflow) - float(total_outflow)
        liquidity_score = min(100, max(0, round((net / (float(total_inflow) + 1)) * 100, 1)))

        # Daily breakdown
        daily = []
        for i in range(days):
            day = start + timedelta(days=i)
            day_qs = qs.filter(transaction_date__date=day)
            inflow = day_qs.filter(transaction_type="inflow").aggregate(s=Sum("amount"))["s"] or 0
            outflow = day_qs.filter(transaction_type="outflow").aggregate(s=Sum("amount"))["s"] or 0
            daily.append({
                "date": day.isoformat(),
                "inflow": float(inflow),
                "outflow": float(outflow),
                "net": float(inflow) - float(outflow),
            })

        return Response({
            "period_days": days,
            "total_inflow": float(total_inflow),
            "total_outflow": float(total_outflow),
            "net_cashflow": net,
            "liquidity_score": liquidity_score,
            "daily_breakdown": daily,
        })
