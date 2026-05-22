from django.contrib import admin
from .models import AgentLog


@admin.register(AgentLog)
class AgentLogAdmin(admin.ModelAdmin):
    list_display = ("agent_name", "status", "pipeline_run_id", "execution_time_ms", "created_at")
    list_filter = ("agent_name", "status")
    search_fields = ("pipeline_run_id",)
    ordering = ("-created_at",)
