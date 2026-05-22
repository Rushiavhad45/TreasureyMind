from django.contrib import admin
from .models import Forecast, ForecastDataPoint


@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("id", "forecast_type", "status", "forecast_period_start", "forecast_period_end", "created_at")
    list_filter = ("forecast_type", "status")
    ordering = ("-created_at",)


@admin.register(ForecastDataPoint)
class ForecastDataPointAdmin(admin.ModelAdmin):
    list_display = ("forecast", "date", "predicted_inflow", "predicted_outflow", "predicted_net")
    ordering = ("forecast", "date")
