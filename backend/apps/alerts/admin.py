from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("title", "alert_type", "severity", "is_acknowledged", "created_at")
    list_filter = ("alert_type", "severity", "is_acknowledged")
    search_fields = ("title", "message")
    ordering = ("-created_at",)
