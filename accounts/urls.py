from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('me/', views.current_user, name='current_user'),
    path('audit-logs/', views.audit_log_list, name='audit_logs'),
]