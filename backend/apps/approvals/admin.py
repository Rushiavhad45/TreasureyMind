from django.contrib import admin
from .models import Approval, AuditLog


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ("title", "approval_type", "status", "requested_by", "decided_by", "created_at")
    list_filter = ("approval_type", "status")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "entity_id", "performed_by", "created_at")
    list_filter = ("action", "entity_type")
    search_fields = ("action", "entity_type", "entity_id")
    ordering = ("-created_at",)
