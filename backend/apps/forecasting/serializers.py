from rest_framework import serializers
from .models import Forecast, ForecastDataPoint


class ForecastDataPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastDataPoint
        fields = "__all__"


class ForecastSerializer(serializers.ModelSerializer):
    data_points = ForecastDataPointSerializer(many=True, read_only=True)

    class Meta:
        model = Forecast
        fields = "__all__"
