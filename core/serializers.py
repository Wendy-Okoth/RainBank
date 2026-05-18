from rest_framework import serializers
from .models import Farmer, Farm, Payout, DroughtEvent, CarbonCreditBatch, RainfallRecord

class FarmerSerializer(serializers.ModelSerializer):
    total_farms = serializers.IntegerField(read_only=True)
    total_carbon = serializers.FloatField(read_only=True)
    total_payouts = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Farmer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_seen']

class FarmSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.name', read_only=True)
    drought_risk = serializers.CharField(read_only=True)
    
    class Meta:
        model = Farm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class DroughtEventSerializer(serializers.ModelSerializer):
    farm_details = FarmSerializer(source='farm', read_only=True)
    
    class Meta:
        model = DroughtEvent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'rainfall_percentage', 'severity']

class PayoutSerializer(serializers.ModelSerializer):
    farmer_name = serializers.CharField(source='farmer.name', read_only=True)
    
    class Meta:
        model = Payout
        fields = '__all__'
        read_only_fields = ['requested_at', 'sent_at', 'completed_at', 'failed_at']

class CarbonCreditBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonCreditBatch
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'total_revenue_usd', 'payout_pool_usd', 'farmer_bonus_usd', 'operations_usd']

class RainfallRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = RainfallRecord
        fields = '__all__'