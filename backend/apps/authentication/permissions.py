"""TreasuryMind AI - Custom Permissions"""

from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsApproverRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_approver


class IsTreasuryManagerOrAbove(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            UserRole.ADMIN, UserRole.TREASURY_MANAGER
        ]
