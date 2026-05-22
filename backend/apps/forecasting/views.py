"""
TreasuryMind AI - Forecasting Views & Tasks
"""

from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from celery import shared_task
import logging

from .models import Forecast, ForecastDataPoint, ForecastStatus

logger = logging.getLogger('apps')


# ─── Serializers ──────────────────────────────────────────────────────────────
class ForecastDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastDataPoint
        fields = ['date', 'predicted_inflow', 'predicted_outflow', 'predicted_net',
                  'lower_bound', 'upper_bound']


class ForecastSerializer(serializers.ModelSerializer):
    data_points = ForecastDataPointSerializer(many=True, read_only=True)

    class Meta:
        model = Forecast
        fields = '__all__'


# ─── Views ────────────────────────────────────────────────────────────────────
class ForecastListView(generics.ListAPIView):
    queryset = Forecast.objects.prefetch_related('data_points').all()
    serializer_class = ForecastSerializer
    permission_classes = [IsAuthenticated]


class ForecastDetailView(generics.RetrieveAPIView):
    queryset = Forecast.objects.prefetch_related('data_points').all()
    serializer_class = ForecastSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_forecast(request):
    """Manually trigger a forecast run."""
    from apps.forecasting.tasks import run_forecasting_pipeline
    horizon = request.data.get('horizon_days', 30)
    task = run_forecasting_pipeline.delay(horizon_days=horizon)
    return Response({
        'message': 'Forecast initiated',
        'task_id': task.id
    }, status=status.HTTP_202_ACCEPTED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def latest_forecast(request):
    """Return the most recent completed forecast."""
    forecast = Forecast.objects.filter(
        status=ForecastStatus.COMPLETED
    ).prefetch_related('data_points').first()
    if not forecast:
        return Response({'detail': 'No completed forecast available.'}, status=404)
    return Response(ForecastSerializer(forecast).data)
