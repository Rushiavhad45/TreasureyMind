"""TreasuryMind AI - Approvals Views"""

from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Approval, AuditLog, ApprovalStatus
from apps.authentication.permissions import IsApproverRole


class ApprovalSerializer(serializers.ModelSerializer):
    requested_by_name = serializers.CharField(source='requested_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = Approval
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'


class ApprovalListView(generics.ListAPIView):
    queryset = Approval.objects.select_related('requested_by', 'approved_by').all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'approval_type']
    ordering = ['-created_at']


class ApprovalDetailView(generics.RetrieveAPIView):
    queryset = Approval.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApproverRole])
def decide_approval(request, pk):
    """Approve or reject an approval request."""
    try:
        approval = Approval.objects.get(pk=pk)
    except Approval.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    decision = request.data.get('decision')
    comments = request.data.get('comments', '')

    if decision not in ['approved', 'rejected']:
        return Response({'detail': 'decision must be "approved" or "rejected"'}, status=400)

    if approval.status != ApprovalStatus.PENDING:
        return Response({'detail': 'Approval already decided'}, status=400)

    old_status = approval.status
    approval.status = decision
    approval.approved_by = request.user
    approval.comments = comments
    approval.decided_at = timezone.now()
    approval.save()

    # Create audit log
    AuditLog.objects.create(
        action=f'approval_{decision}',
        entity_type='Approval',
        entity_id=str(approval.id),
        description=f'Approval {decision} by {request.user.get_full_name()}. Comments: {comments}',
        performed_by=request.user,
        old_values={'status': old_status},
        new_values={'status': decision, 'comments': comments},
    )

    return Response(ApprovalSerializer(approval).data)


class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('performed_by').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'entity_type']
    ordering = ['-timestamp']
