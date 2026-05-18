from django.db import models
from core.models import Farmer, Payout

class MpesaTransaction(models.Model):
    """Model to store M-Pesa transactions (placeholder for future integration)"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Transaction details
    transaction_id = models.CharField(max_length=50, unique=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_desc = models.CharField(max_length=200, blank=True)
    
    # Amount and recipient
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    
    # Relationships
    farmer = models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, blank=True)
    payout = models.OneToOneField(Payout, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.amount} KES - {self.status}"

class PaymentWebhook(models.Model):
    """Store incoming webhooks from M-Pesa"""
    
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True)
    
    def __str__(self):
        return f"Webhook at {self.received_at}"