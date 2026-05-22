"""TreasuryMind AI - Allocation Views"""

from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Allocation


class AllocationSerializer(serializers.ModelSerializer):
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = Allocation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AllocationListView(generics.ListAPIView):
    queryset = Allocation.objects.select_related('approved_by').all()
    serializer_class = AllocationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'risk_level']
    ordering = ['priority', '-created_at']


class AllocationDetailView(generics.RetrieveAPIView):
    queryset = Allocation.objects.all()
    serializer_class = AllocationSerializer
    permission_classes = [IsAuthenticated]
