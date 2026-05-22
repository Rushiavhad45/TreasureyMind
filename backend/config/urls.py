"""
TreasuryMind AI - URL Configuration
All API routes are prefixed with /api/v1/
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="TreasuryMind AI API",
        default_version='v1',
        description="Multi-Agent Treasury & Cash Flow Optimization Platform API",
        contact=openapi.Contact(email="api@treasurymind.ai"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API v1 Routes
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/transactions/', include('apps.transactions.urls')),
    path('api/v1/cashflow/', include('apps.cashflow.urls')),
    path('api/v1/forecasting/', include('apps.forecasting.urls')),
    path('api/v1/allocation/', include('apps.allocation.urls')),
    path('api/v1/alerts/', include('apps.alerts.urls')),
    path('api/v1/approvals/', include('apps.approvals.urls')),
    path('api/v1/agents/', include('apps.agents.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]
