# backend/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Public pages (Frontend)
    path('', views.landing_page, name='landing'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-pin/', views.forgot_pin_page, name='forgot_pin'),
    # Add to urlpatterns
    path('switch-language/', views.switch_language, name='switch_language'),
    
    # Dashboard pages (after login)
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/drought-status/', views.dashboard_drought_status, name='dashboard_drought_status'),
    path('dashboard/carbon-credits/', views.dashboard_carbon_credits, name='dashboard_carbon_credits'),
    path('dashboard/payout-history/', views.dashboard_payout_history, name='dashboard_payout_history'),
    path('dashboard/farm-map/', views.dashboard_farm_map, name='dashboard_farm_map'),
    path('dashboard/profile/', views.dashboard_profile, name='dashboard_profile'),
    
    # API Endpoints (for AJAX calls)
    path('api/farmers/', views.farmer_list, name='farmer_list'),
    path('api/farmers/<int:farmer_id>/', views.farmer_detail, name='farmer_detail'),
    path('api/farms/', views.farm_list, name='farm_list'),
    path('api/payouts/', views.payout_list, name='payout_list'),
    path('api/carbon-stats/', views.carbon_stats, name='carbon_stats'),
    path('api/dashboard-stats/', views.dashboard_stats, name='dashboard_stats'),
    path('api/register-farmer/', views.register_farmer_api, name='register_farmer_api'),
    path('api/simulate-drought/<int:farm_id>/', views.simulate_drought, name='simulate_drought'),
]