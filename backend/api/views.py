from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import models
from core.models import Farmer, Farm, Payout, DroughtEvent, CarbonCreditBatch
from core.serializers import (
    FarmerSerializer, FarmSerializer, PayoutSerializer, 
    DroughtEventSerializer, CarbonCreditBatchSerializer
)

class FarmerAPIView(APIView):
    """API for Farmer CRUD operations"""
    permission_classes = [AllowAny]  # Change to IsAuthenticated for production
    
    def get(self, request):
        """Get all farmers"""
        farmers = Farmer.objects.filter(is_active=True)
        serializer = FarmerSerializer(farmers, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': len(serializer.data)
        })
    
    def post(self, request):
        """Create a new farmer"""
        serializer = FarmerSerializer(data=request.data)
        if serializer.is_valid():
            farmer = serializer.save()
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Farmer created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class FarmerDetailAPIView(APIView):
    """API for single farmer operations"""
    
    def get(self, request, farmer_id):
        """Get farmer by ID"""
        try:
            farmer = Farmer.objects.get(id=farmer_id, is_active=True)
            serializer = FarmerSerializer(farmer)
            return Response({'success': True, 'data': serializer.data})
        except Farmer.DoesNotExist:
            return Response({'success': False, 'error': 'Farmer not found'}, status=404)
    
    def put(self, request, farmer_id):
        """Update farmer"""
        try:
            farmer = Farmer.objects.get(id=farmer_id)
            serializer = FarmerSerializer(farmer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, 'data': serializer.data})
            return Response({'success': False, 'errors': serializer.errors}, status=400)
        except Farmer.DoesNotExist:
            return Response({'success': False, 'error': 'Farmer not found'}, status=404)
    
    def delete(self, request, farmer_id):
        """Soft delete farmer"""
        try:
            farmer = Farmer.objects.get(id=farmer_id)
            farmer.is_active = False
            farmer.save()
            return Response({'success': True, 'message': 'Farmer deactivated'})
        except Farmer.DoesNotExist:
            return Response({'success': False, 'error': 'Farmer not found'}, status=404)

class FarmAPIView(APIView):
    """API for Farm operations"""
    
    def get(self, request):
        """Get all farms"""
        farms = Farm.objects.filter(is_active=True)
        serializer = FarmSerializer(farms, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    def post(self, request):
        """Create a new farm"""
        serializer = FarmSerializer(data=request.data)
        if serializer.is_valid():
            farm = serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=400)

class PayoutAPIView(APIView):
    """API for Payout operations"""
    
    def get(self, request):
        """Get all payouts"""
        payouts = Payout.objects.filter(status='completed')
        serializer = PayoutSerializer(payouts, many=True)
        return Response({'success': True, 'data': serializer.data})
    
    def post(self, request):
        """Create a manual payout"""
        serializer = PayoutSerializer(data=request.data)
        if serializer.is_valid():
            payout = serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=201)
        return Response({'success': False, 'errors': serializer.errors}, status=400)

class DashboardStatsAPIView(APIView):
    """API for dashboard statistics"""
    
    def get(self, request):
        stats = {
            'total_farmers': Farmer.objects.filter(is_active=True).count(),
            'total_farms': Farm.objects.filter(is_active=True).count(),
            'total_payouts': Payout.objects.filter(status='completed').count(),
            'total_payout_amount': float(Payout.objects.filter(status='completed').aggregate(
                total=models.Sum('amount_kes')
            )['total'] or 0),
            'total_carbon_sequestered': Farm.objects.aggregate(
                total=models.Sum('carbon_sequestered_tons')
            )['total'] or 0,
            'women_farmers': Farmer.objects.filter(gender='F', is_active=True).count(),
            'pwd_farmers': Farmer.objects.filter(has_disability=True, is_active=True).count(),
        }
        return Response(stats)

class CarbonStatsAPIView(APIView):
    """API for carbon credit statistics"""
    
    def get(self, request):
        total_carbon = Farm.objects.aggregate(
            total=models.Sum('carbon_sequestered_tons')
        )['total'] or 0
        
        return Response({
            'total_sequestered_tons': total_carbon,
            'potential_value_usd': total_carbon * 10,
            'price_per_ton_usd': 10,
            'farmers_practicing': Farm.objects.filter(
                regenerative_practices__len__gt=0
            ).count(),
            'methodology': 'Verra VM0042',
        })
