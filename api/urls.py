from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Farmer endpoints
    path('v1/farmers/', views.FarmerAPIView.as_view(), name='farmers'),
    path('v1/farmers/<int:farmer_id>/', views.FarmerDetailAPIView.as_view(), name='farmer_detail'),
    
    # Farm endpoints
    path('v1/farms/', views.FarmAPIView.as_view(), name='farms'),
    
    # Payout endpoints
    path('v1/payouts/', views.PayoutAPIView.as_view(), name='payouts'),
    
    # Stats endpoints
    path('v1/dashboard-stats/', views.DashboardStatsAPIView.as_view(), name='dashboard_stats'),
    path('v1/carbon-stats/', views.CarbonStatsAPIView.as_view(), name='carbon_stats'),
]