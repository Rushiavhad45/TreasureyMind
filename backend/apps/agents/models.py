"""
TreasuryMind AI - Agent Models
Tracks AI agent execution and logs
"""

from django.db import models
import uuid


class AgentName(models.TextChoices):
    CASHFLOW = 'cashflow_agent', 'CashFlow Agent'
    FORECAST = 'forecast_agent', 'Forecast Agent'
    ALLOCATION = 'allocation_agent', 'Allocation Agent'
    RISK_ALERT = 'risk_alert_agent', 'Risk Alert Agent'
    APPROVAL = 'approval_agent', 'Approval Agent'


class AgentStatus(models.TextChoices):
    IDLE = 'idle', 'Idle'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class AgentLog(models.Model):
    """
    Records each agent execution run with inputs, outputs, and timing.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_name = models.CharField(max_length=30, choices=AgentName.choices)
    status = models.CharField(max_length=15, choices=AgentStatus.choices, default=AgentStatus.IDLE)
    task_description = models.TextField()
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    reasoning = models.TextField(blank=True, help_text="AI reasoning chain from Gemini")
    error_message = models.TextField(blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    gemini_tokens_used = models.IntegerField(default=0)
    pipeline_run_id = models.UUIDField(null=True, blank=True, help_text="Groups agents in same pipeline run")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'agent_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['agent_name', 'status']),
            models.Index(fields=['pipeline_run_id']),
        ]

    def __str__(self):
        return f"{self.agent_name} [{self.status}] at {self.started_at}"
