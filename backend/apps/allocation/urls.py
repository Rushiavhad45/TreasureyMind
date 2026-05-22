from django.urls import path
from . import views
urlpatterns = [
    path('', views.AllocationListView.as_view(), name='allocation-list'),
    path('<uuid:pk>/', views.AllocationDetailView.as_view(), name='allocation-detail'),
]
