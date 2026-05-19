from django.contrib import admin
from django.utils.html import format_html
from .models import Farmer, Farm, DroughtEvent, Payout, CarbonCreditBatch, RainfallRecord

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'gender', 'has_disability', 'total_farms_display', 'is_active', 'created_at']
    list_filter = ['gender', 'has_disability', 'is_active', 'registered_via', 'county']
    search_fields = ['name', 'phone_number', 'national_id', 'village']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'phone_number', 'national_id', 'gender', 'date_of_birth')
        }),
        ('Location', {
            'fields': ('village', 'sub_county', 'county')
        }),
        ('Inclusion', {
            'fields': ('has_disability', 'disability_type', 'preferred_language')
        }),
        ('Registration', {
            'fields': ('registered_via', 'mpesa_phone', 'is_active', 'is_verified', 'verification_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_seen'),
            'classes': ('collapse',)
        }),
    )
    
    def total_farms_display(self, obj):
        return obj.total_farms
    total_farms_display.short_description = 'Total Farms'

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ['farmer_link', 'crop_type', 'area_acres', 'carbon_sequestered_tons', 'is_active']
    list_filter = ['crop_type', 'soil_type', 'is_active', 'is_monitored']
    search_fields = ['farmer__name', 'farmer__phone_number', 'landmark', 'name']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['farmer']
    
    def farmer_link(self, obj):
        return format_html('<a href="/admin/core/farmer/{}/">{}</a>', obj.farmer.id, obj.farmer.name)
    farmer_link.short_description = 'Farmer'

@admin.register(DroughtEvent)
class DroughtEventAdmin(admin.ModelAdmin):
    list_display = ['farm_link', 'start_date', 'consecutive_dry_days', 'severity', 'is_triggered', 'triggered_at']
    list_filter = ['severity', 'is_triggered', 'crop_stage_at_event', 'data_source', 'start_date']
    search_fields = ['farm__farmer__name', 'farm__farmer__phone_number']
    readonly_fields = ['created_at', 'updated_at', 'rainfall_percentage']
    date_hierarchy = 'start_date'
    
    def farm_link(self, obj):
        return format_html('<a href="/admin/core/farm/{}/">{}</a>', obj.farm.id, obj.farm)
    farm_link.short_description = 'Farm'

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['farmer_link', 'amount_kes', 'payout_type', 'status', 'sent_at', 'mpesa_transaction_id']
    list_filter = ['status', 'payout_type', 'requested_at']  # FIXED: changed from 'created_at' to 'requested_at'
    search_fields = ['farmer__name', 'farmer__phone_number', 'mpesa_transaction_id']
    readonly_fields = ['requested_at', 'sent_at', 'completed_at', 'failed_at']  # FIXED: changed from 'created_at' to 'requested_at'
    list_editable = ['status']
    raw_id_fields = ['farmer', 'drought_event']
    
    def farmer_link(self, obj):
        return format_html('<a href="/admin/core/farmer/{}/">{}</a>', obj.farmer.id, obj.farmer.name)
    farmer_link.short_description = 'Farmer'

@admin.register(CarbonCreditBatch)
class CarbonCreditBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_id', 'vintage_year', 'total_tons', 'price_per_ton_usd', 'total_revenue_usd', 'status']
    list_filter = ['status', 'vintage_year', 'verification_method']
    search_fields = ['batch_id', 'sold_to']
    readonly_fields = ['created_at', 'updated_at', 'total_revenue_usd', 'payout_pool_usd', 'farmer_bonus_usd', 'operations_usd']

@admin.register(RainfallRecord)
class RainfallRecordAdmin(admin.ModelAdmin):
    list_display = ['farm_link', 'date', 'rainfall_mm', 'source']
    list_filter = ['source', 'date']
    search_fields = ['farm__farmer__name', 'farm__farmer__phone_number']
    date_hierarchy = 'date'
    
    def farm_link(self, obj):
        return format_html('<a href="/admin/core/farm/{}/">{}</a>', obj.farm.id, obj.farm)
    farm_link.short_description = 'Farm'