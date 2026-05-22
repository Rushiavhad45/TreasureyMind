"""
TreasuryMind AI - Alerts Models
"""

from django.db import models
from django.conf import settings
import uuid


class AlertSeverity(models.TextChoices):
    INFO = 'info', 'Info'
    WARNING = 'warning', 'Warning'
    CRITICAL = 'critical', 'Critical'


class AlertType(models.TextChoices):
    LOW_BALANCE = 'low_balance', 'Low Balance'
    HIGH_OUTFLOW = 'high_outflow', 'High Outflow'
    UNUSUAL_TRANSACTION = 'unusual_transaction', 'Unusual Transaction'
    FORECAST_RISK = 'forecast_risk', 'Forecast Risk'
    ALLOCATION_NEEDED = 'allocation_needed', 'Allocation Needed'
    AGENT_UPDATE = 'agent_update', 'Agent Update'


class Alert(models.Model):
    """
    System and AI-generated alerts for treasury events.
    Supports acknowledgment workflow.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, choices=AlertType.choices)
    severity = models.CharField(max_length=10, choices=AlertSeverity.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(default=dict, help_text="Contextual data for the alert")
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    related_transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='alerts'
    )
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read', 'is_resolved']),
            models.Index(fields=['severity']),
        ]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title}"
