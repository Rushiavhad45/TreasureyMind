from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("reference_number", "transaction_type", "category", "amount", "status", "transaction_date")
    list_filter = ("transaction_type", "category", "status")
    search_fields = ("reference_number", "description", "counterparty")
    ordering = ("-transaction_date",)
    date_hierarchy = "transaction_date"
