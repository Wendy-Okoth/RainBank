from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import MpesaTransaction, PaymentWebhook

@csrf_exempt
@require_http_methods(['POST'])
def mpesa_callback(request):
    """Handle M-Pesa callback (placeholder)"""
    try:
        data = json.loads(request.body)
        
        # Store webhook
        webhook = PaymentWebhook.objects.create(payload=data)
        
        # Process webhook (to be implemented)
        # This will be implemented when integrating actual M-Pesa API
        
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
    except Exception as e:
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)}, status=400)

@require_http_methods(['GET'])
def transaction_status(request, transaction_id):
    """Check transaction status"""
    try:
        transaction = MpesaTransaction.objects.get(transaction_id=transaction_id)
        return JsonResponse({
            'transaction_id': transaction.transaction_id,
            'status': transaction.status,
            'amount': str(transaction.amount),
            'phone_number': transaction.phone_number,
            'result_desc': transaction.result_desc,
        })
    except MpesaTransaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)

@require_http_methods(['POST'])
def simulate_payout(request):
    """Simulate a payout for testing (without actual M-Pesa)"""
    try:
        data = json.loads(request.body)
        
        # Create simulated transaction
        transaction = MpesaTransaction.objects.create(
            transaction_id=f"SIM_{request.POST.get('phone_number', '')}_{int(time.time())}",
            amount=data.get('amount'),
            phone_number=data.get('phone_number'),
            status='completed'
        )
        
        return JsonResponse({
            'success': True,
            'transaction_id': transaction.transaction_id,
            'message': 'Simulated payout successful'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
