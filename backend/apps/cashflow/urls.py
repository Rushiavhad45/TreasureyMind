from django.urls import path
from .views import CashFlowSnapshotListView, CashFlowMetricsView

urlpatterns = [
    path("snapshots/", CashFlowSnapshotListView.as_view(), name="cashflow-snapshots"),
    path("metrics/", CashFlowMetricsView.as_view(), name="cashflow-metrics"),
]
