from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import hashlib
from .models import USSDsession, SMSLog
from core.models import Farmer, Farm

@csrf_exempt
@require_http_methods(['POST', 'GET'])
def ussd_handler(request):
    """
    USSD webhook handler for Africa's Talking
    This is a complete USSD menu system for farmer registration
    """
    if request.method == 'POST':
        session_id = request.POST.get('sessionId')
        phone_number = request.POST.get('phoneNumber')
        text = request.POST.get('text', '')
        
        # Get or create session
        session, created = USSDsession.objects.get_or_create(
            session_id=session_id,
            defaults={'phone_number': phone_number}
        )
        
        # Parse USSD input
        if not text:  # First request
            response = "CON Welcome to RainBank!\n"
            response += "Free drought insurance powered by your soil carbon.\n\n"
            response += "1. Register\n"
            response += "2. Check Status\n"
            response += "3. About RainBank\n"
            response += "0. Exit"
            
            session.current_step = 0
            session.save()
            
        elif text == '0':  # Exit
            response = "END Thank you for using RainBank. Goodbye!"
            session.status = 'completed'
            session.ended_at = timezone.now()
            session.save()
            
        elif text == '1':  # Start registration
            response = "CON Enter your full name:"
            session.current_step = 1
            session.save()
            
        elif text == '2':  # Check status
            # Check if farmer exists
            try:
                farmer = Farmer.objects.get(phone_number=phone_number)
                response = f"END Your status:\n"
                response += f"Name: {farmer.name}\n"
                response += f"Farms: {farmer.total_farms}\n"
                response += f"Carbon: {farmer.total_carbon_sequestered} tons\n"
                response += f"Total payouts: KES {farmer.total_payouts_received}"
            except Farmer.DoesNotExist:
                response = "END You are not registered. Dial *384# and select 1 to register."
            
            session.status = 'completed'
            session.save()
            
        elif text == '3':  # About
            response = "END RainBank gives you free drought insurance. "
            response += "When you use manure, mulch, or minimum tillage, "
            response += "your soil captures carbon. We sell that carbon and "
            response += "use the money to pay you when drought strikes. "
            response += "No fees. No paperwork. Dial *384# to register."
            session.status = 'completed'
            session.save()
            
        # Registration flow
        elif session.current_step == 1:  # Got name
            name = text
            session.session_data['name'] = name
            response = "CON Select gender:\n1. Female\n2. Male\n3. Other"
            session.current_step = 2
            session.save()
            
        elif session.current_step == 2:  # Got gender
            gender_map = {'1': 'F', '2': 'M', '3': 'O'}
            gender = gender_map.get(text, 'M')
            session.session_data['gender'] = gender
            response = "CON Enter your county (e.g., Machakos, Kitui, Kiambu):"
            session.current_step = 3
            session.save()
            
        elif session.current_step == 3:  # Got county
            county = text
            session.session_data['county'] = county
            response = "CON Enter your nearest town or village:"
            session.current_step = 4
            session.save()
            
        elif session.current_step == 4:  # Got village
            village = text
            session.session_data['village'] = village
            response = "CON What crop do you grow?\n1. Maize\n2. Beans\n3. Mixed\n4. Vegetables"
            session.current_step = 5
            session.save()
            
        elif session.current_step == 5:  # Got crop
            crop_map = {'1': 'maize', '2': 'beans', '3': 'mixed', '4': 'vegetables'}
            crop = crop_map.get(text, 'maize')
            session.session_data['crop_type'] = crop
            response = "CON How many acres do you farm?\n(Enter number, e.g., 2)"
            session.current_step = 6
            session.save()
            
        elif session.current_step == 6:  # Got acres
            try:
                acres = float(text)
                session.session_data['area_acres'] = acres
            except:
                acres = 1.0
                session.session_data['area_acres'] = 1.0
            
            response = "CON Do you use any of these practices?\n"
            response += "1. Manure\n2. Mulching\n3. Minimum tillage\n"
            response += "4. Cover crops\n5. None\n"
            response += "Select all that apply (e.g., 1,3):"
            session.current_step = 7
            session.save()
            
        elif session.current_step == 7:  # Got practices
            practices_map = {
                '1': 'manure', '2': 'mulching', '3': 'tillage', 
                '4': 'cover', '5': None
            }
            practices = []
            for num in text.split(','):
                practice = practices_map.get(num.strip())
                if practice:
                    practices.append(practice)
            
            # Create farmer
            try:
                farmer = Farmer.objects.create(
                    phone_number=phone_number,
                    name=session.session_data.get('name'),
                    gender=session.session_data.get('gender', 'M'),
                    county=session.session_data.get('county', ''),
                    village=session.session_data.get('village', ''),
                    registered_via='ussd',
                    mpesa_phone=phone_number,
                )
                
                # Create farm
                farm = Farm.objects.create(
                    farmer=farmer,
                    crop_type=session.session_data.get('crop_type', 'maize'),
                    area_acres=session.session_data.get('area_acres', 1),
                    regenerative_practices=practices,
                    carbon_sequestered_tons=session.session_data.get('area_acres', 1) * 1.5,
                )
                
                session.farmer = farmer
                session.status = 'completed'
                session.ended_at = timezone.now()
                session.save()
                
                response = f"END Registration complete! 🌱\n\n"
                response += f"Thank you {farmer.name}! You are now protected by RainBank.\n\n"
                response += f"Your farm: {farm.area_acres} acres of {farm.get_crop_type_display()}\n"
                response += f"Carbon sequestered: {farm.carbon_sequestered_tons} tons/year\n\n"
                response += "We'll monitor rainfall using satellites.\n"
                response += "If drought strikes, we'll send money to your M-Pesa automatically.\n\n"
                response += "No fees. No paperwork. Just peace of mind.\n"
                response += "Dial *384# anytime to check your status."
                
                # Log SMS (would send actual SMS in production)
                SMSLog.objects.create(
                    phone_number=phone_number,
                    message=response[4:],  # Remove 'END ' prefix
                    direction='outgoing',
                    farmer=farmer,
                    sent=True
                )
                
            except Exception as e:
                response = f"END Registration failed. Please try again or call 0800-RAINBANK. Error: {str(e)}"
                
        else:
            response = "END Invalid option. Dial *384# to start over."
            session.status = 'completed'
            session.save()
        
        return JsonResponse({'response': response})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@require_http_methods(['POST'])
def sms_handler(request):
    """Handle incoming SMS (placeholder)"""
    try:
        data = request.POST if request.POST else json.loads(request.body)
        
        phone_number = data.get('phoneNumber')
        message = data.get('text')
        
        # Log incoming SMS
        SMSLog.objects.create(
            phone_number=phone_number,
            message=message,
            direction='incoming'
        )
        
        # Auto-respond to common queries
        if 'balance' in message.lower() or 'status' in message.lower():
            try:
                farmer = Farmer.objects.get(phone_number=phone_number)
                response = f"Your RainBank status:\n"
                response += f"Active farms: {farmer.total_farms}\n"
                response += f"Carbon sequestered: {farmer.total_carbon_sequestered} tons\n"
                response += f"Total payouts: KES {farmer.total_payouts_received}\n"
                response += f"Dial *384# for full menu"
                
                SMSLog.objects.create(
                    phone_number=phone_number,
                    message=response,
                    direction='outgoing',
                    farmer=farmer,
                    sent=True
                )
                
            except Farmer.DoesNotExist:
                response = "You are not registered. Dial *384# to register for free drought insurance."
                
            return JsonResponse({'response': response})
        
        return JsonResponse({'message': 'SMS received'})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(['GET'])
def ussd_sessions(request):
    """Get active USSD sessions (for monitoring)"""
    sessions = USSDsession.objects.filter(status='active')[:50]
    return JsonResponse({
        'active_sessions': [{
            'session_id': s.session_id,
            'phone_number': s.phone_number,
            'current_step': s.current_step,
            'started_at': s.started_at.isoformat(),
        } for s in sessions]
    })