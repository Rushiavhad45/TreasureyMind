from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApprovalListView.as_view(), name='approval-list'),
    path('<uuid:pk>/', views.ApprovalDetailView.as_view(), name='approval-detail'),
    path('<uuid:pk>/decide/', views.decide_approval, name='approval-decide'),
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
]
