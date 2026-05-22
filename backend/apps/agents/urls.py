from django.urls import path
from . import views

urlpatterns = [
    path('logs/', views.AgentLogListView.as_view(), name='agent-logs'),
    path('status/', views.agent_status, name='agent-status'),
    path('trigger/', views.trigger_pipeline, name='agent-trigger'),
]
