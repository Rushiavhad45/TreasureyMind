from rest_framework import serializers
from .models import AgentLog


class AgentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentLog
        fields = "__all__"
