"""
TreasuryMind AI - Forecasting Celery Tasks
Implements moving average cash flow forecasting with Gemini AI reasoning
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Avg
import logging
from datetime import timedelta
from decimal import Decimal

logger = logging.getLogger('apps')


@shared_task(bind=True, max_retries=3)
def run_forecasting_pipeline(self, horizon_days=30):
    """
    Main forecasting task.
    1. Pull historical transaction data
    2. Apply moving average model
    3. Get Gemini AI reasoning
    4. Save forecast to DB
    """
    from apps.forecasting.models import Forecast, ForecastDataPoint, ForecastStatus
    from apps.transactions.models import Transaction, TransactionType, TransactionStatus
    from services.gemini_service import GeminiService

    logger.info(f"Starting forecasting pipeline for {horizon_days} days")
    forecast = Forecast.objects.create(
        horizon_days=horizon_days,
        status=ForecastStatus.RUNNING,
        model_type='moving_average'
    )

    try:
        today = timezone.now().date()
        lookback_days = 90

        # Aggregate daily historical data
        history = {}
        for i in range(lookback_days, 0, -1):
            day = today - timedelta(days=i)
            inflow = Transaction.objects.filter(
                transaction_date=day,
                transaction_type=TransactionType.INFLOW,
                status=TransactionStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            outflow = Transaction.objects.filter(
                transaction_date=day,
                transaction_type=TransactionType.OUTFLOW,
                status=TransactionStatus.COMPLETED
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            history[day] = {'inflow': inflow, 'outflow': outflow}

        # Simple 7-day moving average
        days_list = sorted(history.keys())
        window = 7

        data_points = []
        for i in range(horizon_days):
            future_date = today + timedelta(days=i + 1)
            recent_days = days_list[-window:] if len(days_list) >= window else days_list

            avg_inflow = sum(history[d]['inflow'] for d in recent_days) / len(recent_days) if recent_days else Decimal('0')
            avg_outflow = sum(history[d]['outflow'] for d in recent_days) / len(recent_days) if recent_days else Decimal('0')

            # Add slight trend (1% growth per week)
            trend_factor = Decimal('1') + (Decimal('0.01') * (i // 7))
            predicted_inflow = avg_inflow * trend_factor
            predicted_outflow = avg_outflow

            predicted_net = predicted_inflow - predicted_outflow
            margin = abs(predicted_net) * Decimal('0.15')

            data_points.append(ForecastDataPoint(
                forecast=forecast,
                date=future_date,
                predicted_inflow=predicted_inflow.quantize(Decimal('0.01')),
                predicted_outflow=predicted_outflow.quantize(Decimal('0.01')),
                predicted_net=predicted_net.quantize(Decimal('0.01')),
                lower_bound=(predicted_net - margin).quantize(Decimal('0.01')),
                upper_bound=(predicted_net + margin).quantize(Decimal('0.01')),
            ))

        ForecastDataPoint.objects.bulk_create(data_points)

        # Get AI reasoning from Gemini
        try:
            gemini = GeminiService()
            summary_data = {
                'horizon_days': horizon_days,
                'avg_daily_inflow': float(avg_inflow),
                'avg_daily_outflow': float(avg_outflow),
                'trend': 'positive growth',
                'historical_days_analyzed': lookback_days
            }
            ai_reasoning = gemini.get_forecast_reasoning(summary_data)
            forecast.ai_reasoning = ai_reasoning
        except Exception as e:
            logger.warning(f"Gemini reasoning failed: {e}")
            forecast.ai_reasoning = "AI reasoning unavailable - using statistical model only."

        forecast.status = ForecastStatus.COMPLETED
        forecast.save()
        logger.info(f"Forecasting pipeline completed: {forecast.id}")
        return str(forecast.id)

    except Exception as exc:
        forecast.status = ForecastStatus.FAILED
        forecast.error_message = str(exc)
        forecast.save()
        logger.error(f"Forecasting pipeline failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
