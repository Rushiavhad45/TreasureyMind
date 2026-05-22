"""TreasuryMind AI - Agent Views"""

from rest_framework import serializers, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg

from .models import AgentLog


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = '__all__'


class AgentLogListView(generics.ListAPIView):
    serializer_class = AgentLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['agent_name', 'status']

    def get_queryset(self):
        qs = AgentLog.objects.all()
        pipeline_run_id = self.request.query_params.get('pipeline_run_id')
        if pipeline_run_id:
            qs = qs.filter(pipeline_run_id=pipeline_run_id)
        return qs.order_by('-started_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_pipeline(request):
    """Manually trigger the full agent pipeline."""
    from .tasks import run_full_agent_pipeline
    import uuid
    pipeline_run_id = str(uuid.uuid4())
    task = run_full_agent_pipeline.delay(trigger='manual', pipeline_run_id=pipeline_run_id)
    return Response({
        'message': 'Agent pipeline triggered successfully',
        'task_id': task.id,
        'pipeline_run_id': pipeline_run_id,
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def agent_status(request):
    """Get aggregate agent pipeline status and per-agent stats."""
    from .models import AgentName

    agent_stats = {}
    for agent_name, label in AgentName.choices:
        qs = AgentLog.objects.filter(agent_name=agent_name)
        total = qs.count()
        successful = qs.filter(status='completed').count()
        latest = qs.order_by('-started_at').first()
        avg_time = qs.filter(status='completed').aggregate(avg=Avg('duration_seconds'))['avg']
        agent_stats[agent_name] = {
            'label': label,
            'status': latest.status if latest else 'never_run',
            'last_run': latest.started_at if latest else None,
            'total_runs': total,
            'success_rate': round((successful / total * 100), 1) if total > 0 else 0,
            'avg_duration_seconds': round(avg_time, 2) if avg_time else None,
        }

    # Latest pipeline run summary
    latest_log = AgentLog.objects.order_by('-started_at').first()
    latest_run = None
    if latest_log:
        run_logs = AgentLog.objects.filter(pipeline_run_id=latest_log.pipeline_run_id)
        statuses = list(run_logs.values_list('status', flat=True))
        if 'failed' in statuses:
            run_status = 'failed'
        elif all(s == 'completed' for s in statuses):
            run_status = 'completed'
        else:
            run_status = 'partial'
        latest_run = {
            'pipeline_run_id': str(latest_log.pipeline_run_id) if latest_log.pipeline_run_id else None,
            'status': run_status,
            'agent_count': run_logs.count(),
            'started_at': run_logs.order_by('started_at').first().started_at,
        }

    total_runs = AgentLog.objects.values('pipeline_run_id').distinct().count()
    avg_exec = AgentLog.objects.filter(status='completed').aggregate(avg=Avg('duration_seconds'))['avg']

    return Response({
        'agent_stats': agent_stats,
        'latest_run': latest_run,
        'total_pipeline_runs': total_runs,
        'avg_execution_time_seconds': round(avg_exec, 2) if avg_exec else None,
    })
