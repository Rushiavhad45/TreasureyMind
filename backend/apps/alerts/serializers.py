from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    acknowledged_by_email = serializers.CharField(
        source="acknowledged_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = Alert
        fields = "__all__"
