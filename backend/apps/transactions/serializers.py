from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    created_by_email = serializers.CharField(source="created_by.email", read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("id", "reference_number", "created_by", "created_at", "updated_at")

    def create(self, validated_data):
        # Auto-assign creating user from request context
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)
