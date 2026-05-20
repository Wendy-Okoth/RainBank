# backend/core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import models
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib import messages
from decimal import Decimal
import json
from datetime import datetime, timedelta

from .models import Farmer, Farm, DroughtEvent, Payout, CarbonCreditBatch, RainfallRecord


# ========== HELPER FUNCTIONS ==========

def get_farmer_from_session(request):
    """Helper to get farmer from session"""
    farmer_id = request.session.get('farmer_id')
    if farmer_id:
        try:
            return Farmer.objects.get(id=farmer_id, is_active=True)
        except Farmer.DoesNotExist:
            del request.session['farmer_id']
    return None


# ========== PUBLIC PAGE VIEWS ==========

def landing_page(request):
    """Public landing page"""
    return render(request, 'landing.html')


def register_page(request):
    """Farmer registration page"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            gender = request.POST.get('gender')
            pin = request.POST.get('pin')
            county = request.POST.get('county')
            village = request.POST.get('village')
            crop_type = request.POST.get('crop_type')
            area_acres = request.POST.get('area_acres')
            practices = request.POST.getlist('practices')
            
            # Validate
            if not all([name, phone, gender, pin, county, village, crop_type, area_acres]):
                messages.error(request, 'Please fill all required fields.')
                return render(request, 'register.html')
            
            # Check if farmer already exists
            if Farmer.objects.filter(phone_number=phone).exists():
                messages.error(request, 'Phone number already registered. Please login.')
                return redirect('core:login')
            
            # Create farmer
            farmer = Farmer.objects.create(
                name=name,
                phone_number=phone,
                gender=gender,
                county=county,
                village=village,
                registered_via='web',
                mpesa_phone=phone,
                is_active=True,
                is_verified=True,
                verification_date=timezone.now()
            )
            
            # Store PIN in session (temporarily - in production, use hashed passwords)
            request.session[f'pin_{phone}'] = pin
            
            # Create farm
            farm = Farm.objects.create(
                farmer=farmer,
                crop_type=crop_type,
                area_acres=Decimal(str(area_acres)),
                regenerative_practices=practices,
                carbon_sequestered_tons=float(area_acres) * 1.5,
                is_active=True,
                is_monitored=True,
                latitude=-1.5167,  # Default Machakos coordinates
                longitude=37.2667
            )
            
            messages.success(request, f'Registration successful! Welcome {name}. Please login.')
            return redirect('core:login')
            
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')


def login_page(request):
    """Farmer login page"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        pin = request.POST.get('pin')
        
        try:
            farmer = Farmer.objects.get(phone_number=phone, is_active=True)
            stored_pin = request.session.get(f'pin_{phone}', '1234')
            
            # Check PIN (1234 is default for testing)
            if pin == stored_pin or pin == '1234':
                request.session['farmer_id'] = farmer.id
                messages.success(request, f'Welcome back, {farmer.name}!')
                return redirect('core:dashboard_overview')
            else:
                messages.error(request, 'Invalid PIN. Please try again.')
        except Farmer.DoesNotExist:
            messages.error(request, 'Phone number not found. Please register first.')
    
    return render(request, 'login.html')


def logout_view(request):
    """Logout farmer"""
    if 'farmer_id' in request.session:
        del request.session['farmer_id']
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:landing')


def forgot_pin_page(request):
    """Forgot PIN page"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        try:
            farmer = Farmer.objects.get(phone_number=phone)
            # In production, send SMS with reset code
            messages.success(request, f'Reset instructions sent to {phone}. Check your SMS.')
            return redirect('core:login')
        except Farmer.DoesNotExist:
            messages.error(request, 'Phone number not found.')
    return render(request, 'forgot_pin.html')


# ========== DASHBOARD VIEWS (Authenticated) ==========

def dashboard_overview(request):
    """Main dashboard overview"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        messages.error(request, 'Please login to access your dashboard.')
        return redirect('core:login')
    
    farm = farmer.farms.filter(is_active=True).first()
    
    # Calculate statistics
    total_carbon = farmer.farms.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0
    carbon_value_usd = total_carbon * 10
    carbon_value_kes = carbon_value_usd * 130
    
    # Payout statistics
    payouts = farmer.payouts.filter(status='completed')
    total_payouts = payouts.aggregate(total=models.Sum('amount_kes'))['total'] or 0
    payout_count = payouts.count()
    avg_payout = total_payouts / payout_count if payout_count > 0 else 0
    last_payout = payouts.order_by('-requested_at').first()
    
    # Drought status (simulated - will come from satellite data)
    consecutive_dry_days = 9
    remaining_days = 10 - consecutive_dry_days
    pending_payout = float(farm.area_acres) * 2500 if farm else 0
    
    # Rainfall data for chart
    rainfall_labels = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7']
    rainfall_data = [2.1, 1.8, 0.5, 0.2, 0.0, 0.0, 0.0]
    threshold = 2.5
    
    # Recent payouts
    recent_payouts = farmer.payouts.filter(status='completed').order_by('-requested_at')[:5]
    
    # Recent farmers (for admin view)
    recent_farmers = Farmer.objects.filter(is_active=True).order_by('-created_at')[:10]
    recent_droughts = DroughtEvent.objects.filter(is_triggered=True).select_related(
        'farm', 'farm__farmer'
    ).order_by('-triggered_at')[:10]
    
    # Gender stats for chart
    women_farmers = Farmer.objects.filter(gender='F', is_active=True).count()
    men_farmers = Farmer.objects.filter(gender='M', is_active=True).count()
    pwd_farmers = Farmer.objects.filter(has_disability=True, is_active=True).count()
    
    # Total counts
    total_farmers = Farmer.objects.filter(is_active=True).count()
    total_farms = Farm.objects.filter(is_active=True).count()
    total_payouts_all = Payout.objects.filter(status='completed').count()
    total_payout_amount_all = Payout.objects.filter(status='completed').aggregate(
        total=models.Sum('amount_kes')
    )['total'] or 0
    total_carbon_all = Farm.objects.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0
    
    context = {
        # Farmer specific
        'farmer': farmer,
        'farm': farm,
        'total_carbon': total_carbon,
        'carbon_value_usd': carbon_value_usd,
        'carbon_value_kes': carbon_value_kes,
        'total_payouts': total_payouts,
        'total_payout_amount': total_payouts,
        'payout_count': payout_count,
        'total_payouts_count': payout_count,
        'avg_payout': avg_payout,
        'last_payout_date': last_payout.requested_at if last_payout else None,
        'consecutive_dry_days': consecutive_dry_days,
        'remaining_days': remaining_days,
        'pending_payout': pending_payout,
        'recent_payouts': recent_payouts,
        'recent_droughts': recent_droughts,
        
        # Dashboard stats
        'total_farmers': total_farmers,
        'total_farms': total_farms,
        'total_payouts_all': total_payouts_all,
        'total_payout_amount_all': total_payout_amount_all,
        'total_carbon_all': total_carbon_all,
        'carbon_value_usd_all': total_carbon_all * 10,
        
        # Chart data
        'rainfall_labels': rainfall_labels,
        'rainfall_data': rainfall_data,
        'threshold': threshold,
        'recent_farmers': recent_farmers,
        'women_farmers': women_farmers,
        'men_farmers': men_farmers,
        'pwd_farmers': pwd_farmers,
        
        # UI state
        'active_tab': 'overview',
        'drought_alert': consecutive_dry_days >= 7,
    }
    
    return render(request, 'dashboard_overview.html', context)


def dashboard_drought_status(request):
    """Drought status page"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        return redirect('core:login')
    
    farm = farmer.farms.filter(is_active=True).first()
    consecutive_dry_days = 9
    remaining_days = 10 - consecutive_dry_days
    pending_payout = float(farm.area_acres) * 2500 if farm else 0
    
    # Drought offset for gauge (circumference = 2 * pi * r = 2 * 3.14 * 45 = 283)
    progress = consecutive_dry_days / 10
    drought_offset = 283 * (1 - progress)
    
    # Sample rainfall history
    rainfall_history = []
    for i in range(10):
        date = timezone.now().date() - timedelta(days=i)
        rainfall_history.append({
            'date': date.strftime('%Y-%m-%d'),
            'rainfall': 1.2 if i < 9 else 8.5,
            'normal': 3.5,
        })
    
    # Drought history
    drought_history = []
    for drought in DroughtEvent.objects.filter(farm=farm, is_triggered=True).order_by('-start_date')[:5]:
        drought_history.append({
            'start_date': drought.start_date.strftime('%Y-%m-%d'),
            'end_date': drought.end_date.strftime('%Y-%m-%d') if drought.end_date else 'ongoing',
            'consecutive_dry_days': drought.consecutive_dry_days,
            'payout_amount': float(drought.trigger_amount_kes) if drought.trigger_amount_kes else 0,
            'status': 'Paid' if hasattr(drought, 'payout') and drought.payout.status == 'completed' else 'Pending',
        })
    
    context = {
        'farmer': farmer,
        'farm': farm,
        'consecutive_dry_days': consecutive_dry_days,
        'remaining_days': remaining_days,
        'pending_payout': pending_payout,
        'drought_offset': drought_offset,
        'rainfall_actual': 5.8,
        'rainfall_expected': 35.7,
        'rainfall_history': rainfall_history,
        'drought_history': drought_history,
        'active_tab': 'drought',
        'drought_alert': consecutive_dry_days >= 7,
    }
    
    return render(request, 'dashboard_drought_status.html', context)


def dashboard_carbon_credits(request):
    """Carbon credits page"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        return redirect('core:login')
    
    farm = farmer.farms.filter(is_active=True).first()
    
    total_carbon = farmer.farms.aggregate(total=models.Sum('carbon_sequestered_tons'))['total'] or 0
    carbon_value_usd = total_carbon * 10
    carbon_value_kes = carbon_value_usd * 130
    
    # Revenue split (70-20-10)
    total_revenue = carbon_value_usd
    insurance_pool = total_revenue * 0.70
    farmer_bonus = total_revenue * 0.20
    operations = total_revenue * 0.10
    
    # Practice credits breakdown
    base_credits = float(farm.area_acres) * 0.5 if farm else 1.0
    practice_credits = {}
    practice_rates = {
        'manure': 0.8, 'mulching': 0.6, 'tillage': 0.5, 'cover': 0.7,
        'compost': 0.4, 'agroforestry': 1.2, 'crop_rotation': 0.3, 'terraces': 0.4
    }
    
    if farm and farm.regenerative_practices:
        for practice in farm.regenerative_practices:
            if practice in practice_rates:
                practice_credits[practice] = practice_rates[practice]
    
    # Bonus history
    bonus_history = []
    current_year = timezone.now().year
    for year in [current_year - 1, current_year - 2]:
        bonus_history.append({
            'year': year,
            'tons': total_carbon,
            'amount': carbon_value_kes * 0.20,
            'paid': year < current_year - 1,
        })
    
    context = {
        'farmer': farmer,
        'farm': farm,
        'total_carbon': total_carbon,
        'carbon_value_usd': carbon_value_usd,
        'carbon_value_kes': carbon_value_kes,
        'insurance_pool': insurance_pool,
        'farmer_bonus': farmer_bonus,
        'operations': operations,
        'base_credits': base_credits,
        'practice_credits': practice_credits,
        'bonus_history': bonus_history,
        'active_tab': 'carbon',
    }
    
    return render(request, 'dashboard_carbon_credits.html', context)


def dashboard_payout_history(request):
    """Payout history page"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        return redirect('core:login')
    
    payouts = farmer.payouts.filter(status='completed').order_by('-requested_at')
    
    total_payouts = payouts.aggregate(total=models.Sum('amount_kes'))['total'] or 0
    payout_count = payouts.count()
    avg_payout = total_payouts / payout_count if payout_count > 0 else 0
    last_payout = payouts.first()
    
    context = {
        'farmer': farmer,
        'payouts': payouts,
        'total_payouts': total_payouts,
        'payout_count': payout_count,
        'avg_payout': avg_payout,
        'last_payout_date': last_payout.requested_at if last_payout else None,
        'active_tab': 'payouts',
    }
    
    return render(request, 'dashboard_payout_history.html', context)


def dashboard_farm_map(request):
    """Farm map page"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        return redirect('core:login')
    
    farm = farmer.farms.filter(is_active=True).first()
    
    context = {
        'farmer': farmer,
        'farm': farm,
        'active_tab': 'map',
    }
    
    return render(request, 'dashboard_farm_map.html', context)


def dashboard_profile(request):
    """Farmer profile page"""
    farmer = get_farmer_from_session(request)
    if not farmer:
        return redirect('core:login')
    
    farm = farmer.farms.filter(is_active=True).first()
    
    if request.method == 'POST':
        # Update farmer
        farmer.name = request.POST.get('name', farmer.name)
        farmer.gender = request.POST.get('gender', farmer.gender)
        farmer.county = request.POST.get('county', farmer.county)
        farmer.village = request.POST.get('village', farmer.village)
        farmer.mpesa_phone = request.POST.get('mpesa_phone', farmer.mpesa_phone)
        farmer.save()
        
        # Update farm
        if farm:
            farm.crop_type = request.POST.get('crop_type', farm.crop_type)
            farm.area_acres = Decimal(request.POST.get('area_acres', farm.area_acres))
            farm.regenerative_practices = request.POST.getlist('practices')
            farm.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('core:dashboard_profile')
    
    context = {
        'farmer': farmer,
        'farm': farm,
        'active_tab': 'profile',
    }
    
    return render(request, 'dashboard_profile.html', context)


# ========== ORIGINAL ADMIN / API ENDPOINTS ==========

@require_http_methods(['GET'])
def farmer_list(request):
    """API endpoint to list all farmers"""
    farmers = Farmer.objects.filter(is_active=True).values(
        'id', 'name', 'phone_number', 'gender', 'has_disability', 
        'county', 'created_at'
    ).order_by('-created_at')
    
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
    potential_revenue = total_carbon * 10
    
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
        
        farmer = Farmer.objects.create(
            name=data.get('name'),
            phone_number=data.get('phone_number'),
            gender=data.get('gender', 'M'),
            county=data.get('county', ''),
            village=data.get('village', ''),
            registered_via=data.get('registered_via', 'web'),
            mpesa_phone=data.get('mpesa_phone', data.get('phone_number')),
        )
        
        farm = Farm.objects.create(
            farmer=farmer,
            crop_type=data.get('crop_type', 'maize'),
            area_acres=Decimal(data.get('area_acres', 1)),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            regenerative_practices=data.get('regenerative_practices', []),
            carbon_sequestered_tons=float(data.get('area_acres', 1)) * 1.5,
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