"""
TreasuryMind AI - Approvals & Audit Logs Models
"""

from django.db import models
from django.conf import settings
import uuid


class ApprovalStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    ESCALATED = 'escalated', 'Escalated'


class ApprovalType(models.TextChoices):
    ALLOCATION = 'allocation', 'Fund Allocation'
    LARGE_TRANSACTION = 'large_transaction', 'Large Transaction'
    AGENT_RECOMMENDATION = 'agent_recommendation', 'Agent Recommendation'


class Approval(models.Model):
    """
    Approval workflow for AI suggestions and large transactions.
    All actions are recorded in AuditLog.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_type = models.CharField(max_length=30, choices=ApprovalType.choices)
    status = models.CharField(max_length=15, choices=ApprovalStatus.choices,
                              default=ApprovalStatus.PENDING)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True,
        related_name='requested_approvals'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='handled_approvals'
    )
    comments = models.TextField(blank=True)
    reference_id = models.UUIDField(null=True, blank=True, help_text="ID of the related object")
    reference_model = models.CharField(max_length=50, blank=True)
    due_date = models.DateField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'approvals'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.title}"


class AuditLog(models.Model):
    """
    Immutable audit trail for all significant system actions.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=100)
    description = models.TextField()
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True,
        related_name='audit_logs'
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    old_values = models.JSONField(default=dict)
    new_values = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.entity_type} at {self.timestamp}"
