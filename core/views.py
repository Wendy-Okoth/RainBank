from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import models
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta

from .models import Farmer, Farm, DroughtEvent, Payout, CarbonCreditBatch, RainfallRecord

def dashboard(request):
    """Main dashboard with statistics"""
    
    # Statistics
    total_farmers = Farmer.objects.filter(is_active=True).count()
    total_farms = Farm.objects.filter(is_active=True).count()
    total_payouts = Payout.objects.filter(status='completed').count()
    total_payout_amount = Payout.objects.filter(status='completed').aggregate(
        total=models.Sum('amount_kes')
    )['total'] or 0
    total_carbon = Farm.objects.aggregate(
        total=models.Sum('carbon_sequestered_tons')
    )['total'] or 0
    
    # Recent data
    recent_payouts = Payout.objects.select_related('farmer').filter(
        status='completed'
    ).order_by('-sent_at')[:10]
    
    recent_farmers = Farmer.objects.filter(is_active=True).order_by('-created_at')[:10]
    
    recent_droughts = DroughtEvent.objects.filter(is_triggered=True).select_related(
        'farm', 'farm__farmer'
    ).order_by('-triggered_at')[:10]
    
    # Gender statistics
    women_farmers = Farmer.objects.filter(gender='F', is_active=True).count()
    men_farmers = Farmer.objects.filter(gender='M', is_active=True).count()
    
    # Disability statistics
    pwd_farmers = Farmer.objects.filter(has_disability=True, is_active=True).count()
    
    context = {
        'total_farmers': total_farmers,
        'total_farms': total_farms,
        'total_payouts': total_payouts,
        'total_payout_amount': total_payout_amount,
        'total_carbon': total_carbon,
        'recent_payouts': recent_payouts,
        'recent_farmers': recent_farmers,
        'recent_droughts': recent_droughts,
        'women_farmers': women_farmers,
        'men_farmers': men_farmers,
        'pwd_farmers': pwd_farmers,
        'carbon_value_usd': total_carbon * 10,
    }
    
    return render(request, 'core/dashboard.html', context)

@require_http_methods(['GET'])
def farmer_list(request):
    """API endpoint to list all farmers"""
    farmers = Farmer.objects.filter(is_active=True).values(
        'id', 'name', 'phone_number', 'gender', 'has_disability', 
        'county', 'created_at'
    ).order_by('-created_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(farmers, 20)
    page_obj = paginator.get_page(page)
    
    return JsonResponse({
        'farmers': list(page_obj),
        'total': paginator.count,
        'page': page,
        'total_pages': paginator.num_pages,
    })

@require_http_methods(['GET'])
def farmer_detail(request, farmer_id):
    """Get detailed information about a specific farmer"""
    farmer = get_object_or_404(Farmer, id=farmer_id, is_active=True)
    
    farms = farmer.farms.filter(is_active=True).values(
        'id', 'crop_type', 'area_acres', 'carbon_sequestered_tons'
    )
    
    payouts = farmer.payouts.filter(status='completed').values(
        'amount_kes', 'payout_type', 'sent_at'
    )[:20]
    
    return JsonResponse({
        'id': farmer.id,
        'name': farmer.name,
        'phone_number': farmer.phone_number,
        'gender': farmer.gender,
        'has_disability': farmer.has_disability,
        'disability_type': farmer.disability_type,
        'county': farmer.county,
        'village': farmer.village,
        'registered_via': farmer.registered_via,
        'total_farms': len(farms),
        'farms': list(farms),
        'total_payouts': len(payouts),
        'payouts': list(payouts),
        'total_carbon': farmer.total_carbon_sequestered,
        'total_payouts_received': float(farmer.total_payouts_received),
    })

@require_http_methods(['GET'])
def farm_list(request):
    """API endpoint to list all farms"""
    farms = Farm.objects.filter(is_active=True).select_related('farmer').values(
        'id', 'farmer__name', 'farmer__phone_number', 'crop_type', 
        'area_acres', 'carbon_sequestered_tons', 'latitude', 'longitude'
    )
    
    return JsonResponse({'farms': list(farms)})

@require_http_methods(['GET'])
def payout_list(request):
    """API endpoint to list all payouts"""
    payouts = Payout.objects.filter(status='completed').select_related(
        'farmer', 'drought_event'
    ).values(
        'id', 'farmer__name', 'amount_kes', 'payout_type', 
        'sent_at', 'mpesa_transaction_id'
    ).order_by('-sent_at')[:100]
    
    return JsonResponse({'payouts': list(payouts)})

@require_http_methods(['GET'])
def carbon_stats(request):
    """API endpoint for carbon credit statistics"""
    total_carbon = Farm.objects.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0
    
    # Calculate potential revenue
    potential_revenue = total_carbon * 10
    
    # Get sold credits
    sold_batches = CarbonCreditBatch.objects.filter(status='sold')
    sold_credits = sold_batches.aggregate(total=models.Sum('total_tons'))['total'] or 0
    sold_revenue = sold_batches.aggregate(total=models.Sum('total_revenue_usd'))['total'] or 0
    
    return JsonResponse({
        'total_sequestered_tons': total_carbon,
        'potential_value_usd': potential_revenue,
        'sold_credits_tons': sold_credits,
        'sold_revenue_usd': sold_revenue,
        'price_per_ton_usd': 10,
        'farmers_practicing': Farm.objects.filter(
            regenerative_practices__len__gt=0
        ).count(),
        'methodology': 'Verra VM0042 (Soil Organic Carbon Framework)',
        'last_updated': timezone.now().isoformat(),
    })

@require_http_methods(['GET'])
def dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    return JsonResponse({
        'total_farmers': Farmer.objects.filter(is_active=True).count(),
        'total_farms': Farm.objects.filter(is_active=True).count(),
        'total_payouts': Payout.objects.filter(status='completed').count(),
        'total_payout_amount': float(Payout.objects.filter(status='completed').aggregate(
            total=models.Sum('amount_kes')
        )['total'] or 0),
        'total_carbon': Farm.objects.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0,
        'women_farmers': Farmer.objects.filter(gender='F', is_active=True).count(),
        'pwd_farmers': Farmer.objects.filter(has_disability=True, is_active=True).count(),
        'active_farms': Farm.objects.filter(is_active=True).count(),
    })

@csrf_exempt
@require_http_methods(['POST'])
def register_farmer_api(request):
    """API endpoint to register a farmer (for testing/development)"""
    try:
        data = json.loads(request.body)
        
        # Create farmer
        farmer = Farmer.objects.create(
            name=data.get('name'),
            phone_number=data.get('phone_number'),
            gender=data.get('gender', 'M'),
            county=data.get('county', ''),
            village=data.get('village', ''),
            registered_via=data.get('registered_via', 'web'),
            mpesa_phone=data.get('mpesa_phone', data.get('phone_number')),
        )
        
        # Create farm
        farm = Farm.objects.create(
            farmer=farmer,
            crop_type=data.get('crop_type', 'maize'),
            area_acres=Decimal(data.get('area_acres', 1)),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            regenerative_practices=data.get('regenerative_practices', []),
            carbon_sequestered_tons=data.get('area_acres', 1) * 1.5,  # Estimate: 1.5 tons/acre/year
        )
        
        return JsonResponse({
            'success': True,
            'farmer_id': farmer.id,
            'farm_id': farm.id,
            'message': 'Farmer registered successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(['POST'])
def simulate_drought(request, farm_id):
    """Endpoint to simulate a drought event for testing"""
    farm = get_object_or_404(Farm, id=farm_id)
    
    # Create drought event
    drought = DroughtEvent.objects.create(
        farm=farm,
        start_date=timezone.now().date() - timedelta(days=10),
        consecutive_dry_days=10,
        rainfall_actual_mm=5.0,
        rainfall_avg_mm=50.0,
        is_triggered=True,
        triggered_at=timezone.now(),
        trigger_amount_kes=Decimal(str(farm.area_acres)) * Decimal('2500'),
        crop_stage_at_event='germination'
    )
    
    # Create payout
    payout = Payout.objects.create(
        drought_event=drought,
        farmer=farm.farmer,
        amount_kes=drought.trigger_amount_kes,
        status='pending'
    )
    
    return JsonResponse({
        'success': True,
        'drought_id': drought.id,
        'payout_id': payout.id,
        'amount_kes': str(payout.amount_kes),
        'message': 'Drought simulation triggered'
    })
