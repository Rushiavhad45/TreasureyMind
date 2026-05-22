"""
TreasuryMind AI - Transaction Models
Core financial transaction storage
"""

from django.db import models
from django.conf import settings
import uuid


class TransactionType(models.TextChoices):
    INFLOW = 'inflow', 'Inflow'
    OUTFLOW = 'outflow', 'Outflow'


class TransactionCategory(models.TextChoices):
    # Inflow categories
    REVENUE = 'revenue', 'Revenue'
    INVESTMENT = 'investment', 'Investment'
    LOAN_RECEIPT = 'loan_receipt', 'Loan Receipt'
    RECEIVABLE_COLLECTION = 'receivable_collection', 'Receivable Collection'
    GRANT = 'grant', 'Grant'

    # Outflow categories
    PAYROLL = 'payroll', 'Payroll'
    VENDOR_PAYMENT = 'vendor_payment', 'Vendor Payment'
    LOAN_REPAYMENT = 'loan_repayment', 'Loan Repayment'
    CAPITAL_EXPENDITURE = 'capex', 'Capital Expenditure'
    OPERATING_EXPENSE = 'opex', 'Operating Expense'
    TAX = 'tax', 'Tax'
    UTILITY = 'utility', 'Utility'
    OTHER = 'other', 'Other'


class TransactionStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    FAILED = 'failed', 'Failed'


class Transaction(models.Model):
    """
    Core transaction model representing all financial movements.
    Each transaction is categorized as inflow or outflow.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_number = models.CharField(max_length=50, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    category = models.CharField(max_length=30, choices=TransactionCategory.choices)
    status = models.CharField(
        max_length=15, choices=TransactionStatus.choices,
        default=TransactionStatus.COMPLETED
    )
    transaction_date = models.DateField()
    counterparty = models.CharField(max_length=255, blank=True, help_text="Payer or payee name")
    account = models.CharField(max_length=100, blank=True, help_text="Bank account or fund")
    tags = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"[{self.transaction_type.upper()}] {self.title} - {self.currency} {self.amount}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            import random
            self.reference_number = f"TM-{self.transaction_date.year}-{random.randint(10000, 99999)}"
        super().save(*args, **kwargs)
