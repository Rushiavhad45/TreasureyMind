from django.db import models
import uuid
class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=50, default='daily')
    content = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'reports'
        ordering = ['-generated_at']
