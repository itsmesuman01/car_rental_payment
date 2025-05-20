from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Payment
import uuid

class InitiatePaymentView(APIView):
    def post(self, request):
        # Extract amount from request data
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())

        # Save the payment in the database
        Payment.objects.create(transaction_id=transaction_id, amount=amount)

        # Prepare eSewa parameters
        esewa_url = "https://esewa.com.np/epay/main"
        params = {
            'amt': amount,
            'pdc': 0,
            'psc': 0,
            'txAmt': 0,
            'tAmt': amount,
            'pid': transaction_id,
            'scd': 'your_merchant_id',  # Replace with your merchant ID
            'su': f'{settings.BASE_URL}/api/payment/success/',
            'fu': f'{settings.BASE_URL}/api/payment/failure/',
        }

        return Response({'esewa_url': esewa_url, 'params': params}, status=status.HTTP_200_OK)

class PaymentSuccessView(APIView):
    def get(self, request):
        transaction_id = request.GET.get('oid')
        status = request.GET.get('status')

        if status == 'Success':
            # Update payment status in the database
            Payment.objects.filter(transaction_id=transaction_id).update(status='Completed')
            return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)

        return Response({'message': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)

class PaymentFailureView(APIView):
    def get(self, request):
        transaction_id = request.GET.get('oid')

        # Update payment status in the database
        Payment.objects.filter(transaction_id=transaction_id).update(status='Failed')

        return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
