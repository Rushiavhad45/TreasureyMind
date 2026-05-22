from rest_framework import serializers
from .models import CashFlowSnapshot


class CashFlowSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashFlowSnapshot
        fields = "__all__"
