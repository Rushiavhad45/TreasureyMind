"""URLs for alerts app"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.AlertListView.as_view(), name='alert-list'),
    path('stats/', views.alert_stats, name='alert-stats'),
    path('<uuid:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    path('<uuid:pk>/acknowledge/', views.acknowledge_alert, name='alert-acknowledge'),
]
