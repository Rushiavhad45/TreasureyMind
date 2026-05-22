"""
TreasuryMind AI - Forecasting Models
Stores AI-generated cash flow predictions
"""

from django.db import models
import uuid


class ForecastStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'


class Forecast(models.Model):
    """
    Stores cash flow forecast runs and their predicted values.
    Each run covers a configurable number of future days.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run_date = models.DateTimeField(auto_now_add=True)
    horizon_days = models.IntegerField(default=30)
    status = models.CharField(max_length=15, choices=ForecastStatus.choices, default=ForecastStatus.PENDING)
    model_type = models.CharField(max_length=50, default='moving_average')
    confidence_level = models.FloatField(default=0.80)
    ai_reasoning = models.TextField(blank=True, help_text="Gemini AI explanation of the forecast")
    error_message = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forecasts'
        ordering = ['-run_date']

    def __str__(self):
        return f"Forecast run {self.run_date.date()} ({self.status})"


class ForecastDataPoint(models.Model):
    """Individual predicted value for a specific date in a forecast run."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast = models.ForeignKey(Forecast, on_delete=models.CASCADE, related_name='data_points')
    date = models.DateField()
    predicted_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    predicted_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    predicted_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lower_bound = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    upper_bound = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        db_table = 'forecast_data_points'
        ordering = ['date']
        unique_together = ['forecast', 'date']

    def __str__(self):
        return f"{self.date}: net {self.predicted_net}"
