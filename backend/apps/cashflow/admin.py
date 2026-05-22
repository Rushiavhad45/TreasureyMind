from django.contrib import admin
from .models import CashFlowSnapshot


@admin.register(CashFlowSnapshot)
class CashFlowSnapshotAdmin(admin.ModelAdmin):
    list_display = ("snapshot_date", "total_inflow", "total_outflow", "net_cashflow", "liquidity_score", "created_at")
    ordering = ("-snapshot_date",)
