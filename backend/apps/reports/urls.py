from django.urls import path
from .views import ReportListView, ReportDetailView

urlpatterns = [
    path("", ReportListView.as_view(), name="report-list"),
    path("<uuid:pk>/", ReportDetailView.as_view(), name="report-detail"),
]
