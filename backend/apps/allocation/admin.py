from django.contrib import admin
from .models import Allocation


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ("id", "surplus_amount", "ai_confidence_score", "risk_level", "status", "created_at")
    list_filter = ("risk_level", "status")
    ordering = ("-created_at",)
