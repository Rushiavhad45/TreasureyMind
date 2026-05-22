from celery import shared_task
@shared_task
def generate_daily_report():
    from apps.reports.models import Report
    from django.utils import timezone
    Report.objects.create(
        title=f"Daily Treasury Report - {timezone.now().date()}",
        report_type='daily',
        content={'generated': str(timezone.now())}
    )
