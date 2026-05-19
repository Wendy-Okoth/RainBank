"""
URL configuration for rainbank project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),           # Main dashboard and core functionality
    path('api/', include('api.urls')),        # REST API endpoints
    path('payments/', include('payments.urls')),  # Payment routes
    path('notifications/', include('notifications.urls')),  # USSD/SMS webhooks
    path('accounts/', include('accounts.urls')),  # User management
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)