from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Farmer(models.Model):
    """Farmer model - main entity in the system"""
    
    GENDER_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
        ('O', 'Other'),
    ]
    
    DISABILITY_CHOICES = [
        ('none', 'None'),
        ('blind', 'Blind/Low Vision'),
        ('deaf', 'Deaf/Hard of Hearing'),
        ('mobility', 'Mobility Impairment'),
        ('cognitive', 'Cognitive Disability'),
        ('other', 'Other'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('sw', 'Kiswahili'),
    ]
    
    REGISTRATION_CHANNELS = [
        ('ussd', 'USSD'),
        ('voice', 'Voice Call'),
        ('sms', 'SMS'),
        ('web', 'Website'),
        ('agent', 'Field Agent'),
    ]
    
    # Basic Information
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, blank=True, unique=True, null=True)
    
    # Demographics
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    date_of_birth = models.DateField(null=True, blank=True)
    village = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    county = models.CharField(max_length=100, blank=True)
    
    # Inclusion fields
    has_disability = models.BooleanField(default=False)
    disability_type = models.CharField(max_length=20, choices=DISABILITY_CHOICES, default='none')
    preferred_language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    
    # Registration & Status
    registered_via = models.CharField(max_length=20, choices=REGISTRATION_CHANNELS, default='ussd')
    mpesa_phone = models.CharField(max_length=15, blank=True, help_text="Phone number for M-Pesa payouts")
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['is_active']),
            models.Index(fields=['county']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.phone_number})"
    
    @property
    def total_farms(self):
        return self.farms.filter(is_active=True).count()
    
    @property
    def total_carbon_sequestered(self):
        return self.farms.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0
    
    @property
    def total_payouts_received(self):
        return self.payouts.filter(status='completed').aggregate(
            total=models.Sum('amount_kes')
        )['total'] or 0


class Farm(models.Model):
    """Farm model - linked to farmer"""
    
    CROP_CHOICES = [
        ('maize', 'Maize'),
        ('beans', 'Beans'),
        ('mixed', 'Mixed Cereals'),
        ('vegetables', 'Vegetables'),
        ('coffee', 'Coffee'),
        ('tea', 'Tea'),
        ('other', 'Other'),
    ]
    
    SOIL_TYPE_CHOICES = [
        ('clay', 'Clay'),
        ('sandy', 'Sandy'),
        ('loam', 'Loam'),
        ('silt', 'Silt'),
        ('other', 'Other'),
    ]
    
    PRACTICE_CHOICES = [
        ('manure', 'Manure Application'),
        ('mulching', 'Mulching'),
        ('tillage', 'Minimum Tillage'),
        ('cover', 'Cover Crops'),
        ('compost', 'Compost'),
        ('agroforestry', 'Agroforestry'),
        ('crop_rotation', 'Crop Rotation'),
        ('terraces', 'Terracing'),
    ]
    
    # Relationships
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    
    # Location
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    landmark = models.CharField(max_length=200, blank=True, help_text="Nearest landmark for farmers without GPS")
    altitude_meters = models.IntegerField(null=True, blank=True)
    
    # Farm details
    name = models.CharField(max_length=100, blank=True)
    crop_type = models.CharField(max_length=20, choices=CROP_CHOICES, default='maize')
    area_acres = models.DecimalField(max_digits=10, decimal_places=2, default=1.0)
    soil_type = models.CharField(max_length=20, choices=SOIL_TYPE_CHOICES, blank=True)
    
    # Regenerative practices
    regenerative_practices = models.JSONField(default=list, help_text="List of regenerative practices used")
    years_practicing = models.IntegerField(default=0, help_text="Years using regenerative practices")
    
    # Carbon credit data
    carbon_sequestered_tons = models.FloatField(default=0.0, help_text="Estimated tons CO2 per year")
    carbon_credits_issued = models.FloatField(default=0.0)
    carbon_credits_sold = models.FloatField(default=0.0)
    last_carbon_assessment = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_monitored = models.BooleanField(default=True, help_text="Whether satellite monitoring is active")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farmer', 'is_active']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.farmer.name}'s {self.get_crop_type_display()} farm ({self.area_acres} acres)"
    
    @property
    def estimated_annual_carbon_value(self):
        return self.carbon_sequestered_tons * 10  # $10 per ton
    
    @property
    def drought_risk_level(self):
        """Calculate drought risk based on location and historical data"""
        if self.latitude and self.longitude:
            return "Medium"
        return "Unknown"


class DroughtEvent(models.Model):
    """Drought events detected by satellite"""
    
    CROP_STAGE_CHOICES = [
        ('planting', 'Planting'),
        ('germination', 'Germination'),
        ('vegetative', 'Vegetative Growth'),
        ('flowering', 'Flowering'),
        ('filling', 'Grain Filling'),
        ('maturation', 'Maturation'),
        ('harvest', 'Harvest'),
    ]
    
    SEVERITY_CHOICES = [
        ('mild', 'Mild (5-10 days dry)'),
        ('moderate', 'Moderate (10-15 days dry)'),
        ('severe', 'Severe (15-20 days dry)'),
        ('extreme', 'Extreme (20+ days dry)'),
    ]
    
    # Relationships
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='drought_events')
    
    # Drought details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    consecutive_dry_days = models.IntegerField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, blank=True)
    
    # Rainfall data
    rainfall_actual_mm = models.FloatField(help_text="Actual rainfall during drought period")
    rainfall_avg_mm = models.FloatField(help_text="30-year average rainfall for same period")
    rainfall_percentage = models.FloatField(default=0, help_text="Actual/AVG * 100")
    
    # Crop stage
    crop_stage_at_event = models.CharField(max_length=20, choices=CROP_STAGE_CHOICES, blank=True)
    
    # Trigger status
    is_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    trigger_amount_kes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Satellite data source
    data_source = models.CharField(max_length=50, default='NASA_POWER')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['farm', 'is_triggered']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"Drought at {self.farm} - {self.start_date} ({self.consecutive_dry_days} days)"
    
    def save(self, *args, **kwargs):
        # Auto-calculate severity based on dry days
        if self.consecutive_dry_days >= 20:
            self.severity = 'extreme'
        elif self.consecutive_dry_days >= 15:
            self.severity = 'severe'
        elif self.consecutive_dry_days >= 10:
            self.severity = 'moderate'
        elif self.consecutive_dry_days >= 5:
            self.severity = 'mild'
        
        # Calculate rainfall percentage
        if self.rainfall_avg_mm > 0:
            self.rainfall_percentage = (self.rainfall_actual_mm / self.rainfall_avg_mm) * 100
        
        super().save(*args, **kwargs)


class Payout(models.Model):
    """Payout records for drought events"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYOUT_TYPE_CHOICES = [
        ('drought', 'Drought Insurance'),
        ('bonus_women', 'Women Empowerment Bonus'),
        ('bonus_pwd', 'PWD Bonus'),
        ('carbon_bonus', 'Carbon Credit Bonus'),
        ('top_up', 'Emergency Top-up'),
    ]
    
    # Relationships
    drought_event = models.OneToOneField(DroughtEvent, on_delete=models.CASCADE, related_name='payout')
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='payouts')
    
    # Payout details
    payout_type = models.CharField(max_length=20, choices=PAYOUT_TYPE_CHOICES, default='drought')
    amount_kes = models.DecimalField(max_digits=10, decimal_places=2)
    
    # M-Pesa details (to be integrated later)
    mpesa_transaction_id = models.CharField(max_length=50, blank=True)
    mpesa_result_code = models.CharField(max_length=10, blank=True)
    mpesa_result_desc = models.CharField(max_length=200, blank=True)
    recipient_phone = models.CharField(max_length=15, blank=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    status_message = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Retry tracking
    retry_count = models.IntegerField(default=0)
    last_retry_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_by = models.CharField(max_length=100, blank=True)  # System or admin
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['farmer', 'status']),
            models.Index(fields=['status', 'requested_at']),
        ]
    
    def __str__(self):
        return f"Payout {self.amount_kes} KES to {self.farmer.name} - {self.status}"
    
    def mark_as_sent(self, transaction_id=None):
        """Mark payout as sent"""
        self.status = 'processing'
        self.sent_at = timezone.now()
        if transaction_id:
            self.mpesa_transaction_id = transaction_id
        self.save(update_fields=['status', 'sent_at', 'mpesa_transaction_id'])
    
    def mark_as_completed(self):
        """Mark payout as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_as_failed(self, error_message):
        """Mark payout as failed"""
        self.status = 'failed'
        self.failed_at = timezone.now()
        self.status_message = error_message
        self.save(update_fields=['status', 'failed_at', 'status_message'])


class CarbonCreditBatch(models.Model):
    """Carbon credit batches sold to buyers"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('listed', 'Listed for Sale'),
        ('sold', 'Sold'),
        ('retired', 'Retired'),
    ]
    
    # Batch information
    batch_id = models.CharField(max_length=50, unique=True)
    vintage_year = models.IntegerField(help_text="Year credits were generated")
    total_tons = models.FloatField()
    
    # Sale information
    sold_to = models.CharField(max_length=100, blank=True)
    price_per_ton_usd = models.DecimalField(max_digits=10, decimal_places=2, default=10)
    total_revenue_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Revenue allocation (70-20-10 split)
    payout_pool_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    farmer_bonus_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    operations_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Verification
    verification_method = models.CharField(max_length=100, default='Verra VM0042')
    verification_body = models.CharField(max_length=100, blank=True)
    verification_date = models.DateField(null=True, blank=True)
    verification_report = models.FileField(upload_to='verification_reports/', blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sold_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-vintage_year', '-created_at']
    
    def __str__(self):
        return f"Batch {self.batch_id} - {self.total_tons} tons @ ${self.price_per_ton_usd}"
    
    def save(self, *args, **kwargs):
        # Calculate revenue and allocation
        self.total_revenue_usd = Decimal(str(self.total_tons)) * self.price_per_ton_usd
        self.payout_pool_usd = self.total_revenue_usd * Decimal('0.70')
        self.farmer_bonus_usd = self.total_revenue_usd * Decimal('0.20')
        self.operations_usd = self.total_revenue_usd * Decimal('0.10')
        super().save(*args, **kwargs)


class RainfallRecord(models.Model):
    """Daily rainfall records from satellite"""
    
    SOURCE_CHOICES = [
        ('NASA_POWER', 'NASA POWER'),
        ('CHIRPS', 'CHIRPS'),
        ('GPM', 'Global Precipitation Measurement'),
        ('ground', 'Ground Station'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='rainfall_records')
    date = models.DateField()
    rainfall_mm = models.FloatField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='NASA_POWER')
    
    # 30-year average for this date (for context)
    thirty_year_avg_mm = models.FloatField(null=True, blank=True)
    
    # Metadata
    fetched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['farm', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['farm', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.farm} - {self.date}: {self.rainfall_mm}mm"
    
    @property
    def is_drought_day(self):
        """Check if this day qualifies as drought day"""
        if self.thirty_year_avg_mm:
            return self.rainfall_mm < (self.thirty_year_avg_mm * 0.7)
        return False