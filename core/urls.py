from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API Endpoints
    path('api/farmers/', views.farmer_list, name='farmer_list'),
    path('api/farmers/<int:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    path('api/farms/', views.farm_list, name='farm_list'),
    path('api/payouts/', views.payout_list, name='payout_list'),
    path('api/carbon-stats/', views.carbon_stats, name='carbon_stats'),
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    
    # Actions
    path('api/register-farmer/', views.register_farmer_api, name='register_farmer_api'),
    path('api/simulate-drought/<int:farm_id>/', views.simulate_drought, name='simulate_drought'),
]