"""
TreasuryMind AI - Allocation Models
AI-suggested fund allocation recommendations
"""

from django.db import models
from django.conf import settings
import uuid


class AllocationStatus(models.TextChoices):
    PENDING = 'pending', 'Pending Approval'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    IMPLEMENTED = 'implemented', 'Implemented'


class Allocation(models.Model):
    """
    Stores AI-generated fund allocation suggestions.
    Each allocation is linked to an approval workflow.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    surplus_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=15, choices=AllocationStatus.choices,
                              default=AllocationStatus.PENDING)
    priority = models.IntegerField(default=1, help_text="1=highest priority")
    ai_confidence_score = models.FloatField(default=0.0, help_text="0-1 confidence from AI model")
    ai_reasoning = models.TextField(blank=True)
    allocation_breakdown = models.JSONField(default=list, help_text="List of {category, amount, rationale}")
    risk_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'), ('medium', 'Medium'), ('high', 'High')
    ], default='medium')
    effective_date = models.DateField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_allocations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'allocations'
        ordering = ['priority', '-created_at']

    def __str__(self):
        return f"[{self.status}] {self.title} - {self.surplus_amount}"
