from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('transaction/<str:transaction_id>/', views.transaction_status, name='transaction_status'),
    path('simulate-payout/', views.simulate_payout, name='simulate_payout'),
]