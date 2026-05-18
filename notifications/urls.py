from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('ussd/', views.ussd_handler, name='ussd_handler'),
    path('sms/', views.sms_handler, name='sms_handler'),
    path('ussd-sessions/', views.ussd_sessions, name='ussd_sessions'),
]