from rest_framework import serializers
from .models import Approval, AuditLog


class ApprovalSerializer(serializers.ModelSerializer):
    requested_by_email = serializers.CharField(source="requested_by.email", read_only=True)
    decided_by_email = serializers.CharField(
        source="decided_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = Approval
        fields = "__all__"
        read_only_fields = ("id", "requested_by", "decided_by", "decided_at", "created_at", "updated_at")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["requested_by"] = request.user
        return super().create(validated_data)


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_email = serializers.CharField(
        source="performed_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = AuditLog
        fields = "__all__"
