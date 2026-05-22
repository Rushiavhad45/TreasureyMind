from django.urls import path
from . import views

urlpatterns = [
    path('', views.ForecastListView.as_view(), name='forecast-list'),
    path('latest/', views.latest_forecast, name='forecast-latest'),
    path('trigger/', views.trigger_forecast, name='forecast-trigger'),
    path('<uuid:pk>/', views.ForecastDetailView.as_view(), name='forecast-detail'),
]
