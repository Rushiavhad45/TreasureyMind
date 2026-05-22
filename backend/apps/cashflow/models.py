"""TreasuryMind AI - CashFlow snapshot models"""
from django.db import models
import uuid

class CashFlowSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot_date = models.DateField()
    total_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_cashflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    liquidity_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'cash_flows'
        ordering = ['-snapshot_date']
    def __str__(self):
        return f"CashFlow {self.snapshot_date}: net={self.net_cashflow}"
