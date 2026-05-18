from django.db import models
from core.models import Farmer

class USSDsession(models.Model):
    """Track USSD sessions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15)
    farmer = models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, blank=True)
    
    current_step = models.IntegerField(default=0)
    session_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.session_id} - {self.phone_number}"

class SMSLog(models.Model):
    """Log all SMS messages sent/received"""
    
    DIRECTION_CHOICES = [
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ]
    
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    farmer = models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status tracking
    sent = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.direction} SMS to {self.phone_number} at {self.created_at}"
