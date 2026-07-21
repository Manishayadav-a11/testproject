from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
import uuid

from .models import Payment
from bookings.models import Booking
from students.models import Student
from common.permissions import IsAdmin, IsStudentOrAdmin, IsInstituteOwnerOrAdmin, IsStudent


def payment_to_dict(p):
    return {
        'id': p.id,
        'booking': p.booking_id,
        'transaction_id': p.transaction_id,
        'payment_method': p.payment_method,
        'amount': float(p.amount),
        'platform_commission': float(p.platform_commission),
        'institute_payout': float(p.institute_payout),
        'status': p.status,
        'refund_amount': float(p.refund_amount),
        'refund_reason': p.refund_reason,
        'paid_at': p.paid_at.isoformat() if p.paid_at else None,
        'refunded_at': p.refunded_at.isoformat() if p.refunded_at else None,
        'created_at': p.created_at.isoformat() if p.created_at else None,
    }


class PaymentListView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        if user.role == 'admin':
            payments = Payment.objects.select_related('booking__student__user', 'booking__course').all()
        elif user.role == 'institute_owner':
            payments = Payment.objects.select_related('booking__student__user', 'booking__course').filter(
                booking__course__branch__institute__owner=user
            )
        elif user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)
            payments = Payment.objects.select_related('booking__student__user', 'booking__course').filter(
                booking__student=student
            )
        else:
            return Response([], status=status.HTTP_200_OK)

        data = [payment_to_dict(p) for p in payments]
        return Response(data, status=status.HTTP_200_OK)


class PaymentCreateView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        data = request.data
        booking_id = data.get('booking')
        payment_method = data.get('payment_method')

        errors = {}
        if not booking_id:
            errors['booking'] = 'This field is required.'
        if not payment_method:
            errors['payment_method'] = 'This field is required.'
        if payment_method and payment_method not in dict(Payment.Method.choices):
            errors['payment_method'] = 'Invalid payment method.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'booking': 'Booking not found.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'detail': 'Student profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.student != student:
            return Response({'detail': 'You can only create payments for your own bookings.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status not in ('pending', 'confirmed'):
            return Response(
                {'booking': 'Booking must be pending or confirmed to initiate payment.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Payment.objects.filter(booking=booking, status='success').exists():
            return Response(
                {'booking': 'A successful payment already exists for this booking.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment(
            booking=booking,
            payment_method=payment_method,
            amount=booking.final_amount,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
        )
        payment.save()

        return Response(payment_to_dict(payment), status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    def get(self, request, id):
        try:
            payment = Payment.objects.select_related(
                'booking__student__user', 'booking__course__branch__institute'
            ).get(pk=id)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role == 'admin':
            pass
        elif user.role == 'institute_owner':
            if payment.booking.course.branch.institute.owner != user:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
            if payment.booking.student != student:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(payment_to_dict(payment), status=status.HTTP_200_OK)


class PaymentProcessView(APIView):
    def post(self, request, id):
        try:
            payment = Payment.objects.select_related(
                'booking__student__user', 'booking__course__branch__institute'
            ).get(pk=id)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You do not have permission to process this payment.'}, status=status.HTTP_403_FORBIDDEN)
            if payment.booking.student != student:
                return Response({'detail': 'You do not have permission to process this payment.'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role not in ('admin', 'institute_owner'):
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

        if payment.status != 'pending':
            return Response(
                {'detail': f"Cannot process a payment with status '{payment.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()

        commission_rate = payment.booking.course.branch.institute.commission_rate
        payment.calculate_commission(commission_rate)
        payment.save(update_fields=[
            'status', 'paid_at', 'platform_commission', 'institute_payout', 'updated_at',
        ])

        booking = payment.booking
        if booking.status == 'pending':
            booking.status = 'confirmed'
            booking.save(update_fields=['status', 'updated_at'])

        return Response(payment_to_dict(payment), status=status.HTTP_200_OK)


class PaymentRefundView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        try:
            payment = Payment.objects.select_related(
                'booking__student__user', 'booking__course'
            ).get(pk=id)
        except Payment.DoesNotExist:
            return Response({'detail': 'Payment not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        refund_amount = data.get('refund_amount')
        refund_reason = data.get('refund_reason', '')

        errors = {}
        if refund_amount is None:
            errors['refund_amount'] = 'This field is required.'
        else:
            try:
                refund_amount = Decimal(str(refund_amount))
            except (ValueError, TypeError):
                errors['refund_amount'] = 'Invalid decimal value.'
        if not refund_reason:
            errors['refund_reason'] = 'This field is required.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if refund_amount <= 0:
            return Response({'refund_amount': 'Refund amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)

        if payment.status not in ('success', 'partially_refunded'):
            return Response(
                {'detail': 'Only successful or partially refunded payments can be refunded.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        remaining = payment.amount - payment.refund_amount
        if refund_amount > remaining:
            return Response(
                {'refund_amount': f'Refund amount cannot exceed remaining balance of {remaining}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.refund_amount += refund_amount
        payment.refund_reason = refund_reason
        payment.refunded_at = timezone.now()

        if payment.refund_amount >= payment.amount:
            payment.status = Payment.Status.REFUNDED
            booking = payment.booking
            booking.status = 'refunded'
            booking.save(update_fields=['status', 'updated_at'])
        else:
            payment.status = Payment.Status.PARTIALLY_REFUNDED

        payment.save(update_fields=[
            'status', 'refund_amount', 'refund_reason', 'refunded_at', 'updated_at',
        ])

        return Response(payment_to_dict(payment), status=status.HTTP_200_OK)


class StudentPaymentsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        payments = Payment.objects.select_related(
            'booking__student__user', 'booking__course'
        ).filter(booking__student=student)
        data = [payment_to_dict(p) for p in payments]
        return Response(data, status=status.HTTP_200_OK)


class InstitutePaymentsView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def get(self, request, institute_id):
        user = request.user
        if user.role == 'admin':
            payments = Payment.objects.select_related(
                'booking__student__user', 'booking__course'
            ).filter(booking__course__branch__institute_id=institute_id)
        else:
            payments = Payment.objects.select_related(
                'booking__student__user', 'booking__course'
            ).filter(
                booking__course__branch__institute__owner=user,
                booking__course__branch__institute_id=institute_id,
            )
        data = [payment_to_dict(p) for p in payments]
        return Response(data, status=status.HTTP_200_OK)
