"""
TreasuryMind AI - Celery Configuration
Handles background task scheduling and async processing
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('treasurymind')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ─── Periodic Task Schedule (Celery Beat) ─────────────────────────────────────
app.conf.beat_schedule = {
    # Run forecasting pipeline every 6 hours
    'run-forecasting-pipeline': {
        'task': 'apps.forecasting.tasks.run_forecasting_pipeline',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Check alerts every 15 minutes
    'check-balance-alerts': {
        'task': 'apps.alerts.tasks.check_and_generate_alerts',
        'schedule': crontab(minute='*/15'),
    },
    # Run full agent orchestration pipeline daily at 8am
    'daily-agent-pipeline': {
        'task': 'apps.agents.tasks.run_full_agent_pipeline',
        'schedule': crontab(minute=0, hour=8),
    },
    # Generate daily report at 7am
    'generate-daily-report': {
        'task': 'apps.reports.tasks.generate_daily_report',
        'schedule': crontab(minute=0, hour=7),
    },
    # Refresh cash flow metrics every hour
    'refresh-cashflow-metrics': {
        'task': 'apps.cashflow.tasks.refresh_cashflow_metrics',
        'schedule': crontab(minute=0),
    },
}
