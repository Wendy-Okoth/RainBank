from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from .models import UserProfile, AuditLog

@csrf_exempt
@require_http_methods(['POST'])
def user_login(request):
    """API endpoint for user login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Log the login
            AuditLog.objects.create(
                user=user,
                action='login',
                model_name='User',
                object_id=str(user.id),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.profile.role,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@require_http_methods(['POST'])
@login_required
def user_logout(request):
    """API endpoint for user logout"""
    user = request.user
    
    AuditLog.objects.create(
        user=user,
        action='logout',
        model_name='User',
        object_id=str(user.id),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logout(request)
    return JsonResponse({'success': True, 'message': 'Logged out successfully'})

@require_http_methods(['GET'])
@login_required
def current_user(request):
    """Get current logged-in user info"""
    return JsonResponse({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'role': request.user.profile.role,
        'permissions': {
            'can_approve_payouts': request.user.profile.can_approve_payouts,
            'can_verify_farmers': request.user.profile.can_verify_farmers,
        }
    })

@require_http_methods(['GET'])
@login_required
def audit_log_list(request):
    """Get audit logs (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    logs = AuditLog.objects.select_related('user').all()[:100]
    
    return JsonResponse({
        'logs': [{
            'user': log.user.username if log.user else 'System',
            'action': log.action,
            'model': log.model_name,
            'object_id': log.object_id,
            'timestamp': log.created_at.isoformat(),
        } for log in logs]
    })

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
