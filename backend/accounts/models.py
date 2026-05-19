from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Extended user profile for admin and agent users"""
    
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('agent', 'Field Agent'),
        ('cooperative_leader', 'Cooperative Leader'),
        ('verifier', 'Carbon Verifier'),
        ('viewer', 'Read-only Viewer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    
    # Personal information
    phone_number = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(max_length=50, blank=True)
    
    # Permissions
    can_approve_payouts = models.BooleanField(default=False)
    can_verify_farmers = models.BooleanField(default=False)
    can_access_api = models.BooleanField(default=True)
    
    # Activity tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__username']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    instance.profile.save()


class AuditLog(models.Model):
    """Audit log for tracking important actions"""
    
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('payout', 'Payout Triggered'),
        ('verify', 'Verification'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50)
    changes = models.JSONField(default=dict, help_text="Record of changes made")
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"
