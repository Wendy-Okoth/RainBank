from rest_framework import serializers
from core.models import Farmer, Farm, Payout, DroughtEvent, CarbonCreditBatch

class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_seen']

class FarmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farm
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = '__all__'
        read_only_fields = ['requested_at', 'sent_at', 'completed_at', 'failed_at']

class DroughtEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroughtEvent
        fields = '__all__'

class CarbonCreditBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonCreditBatch
        fields = '__all__'