from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'booking', 'transaction_id', 'payment_method', 'amount',
        'platform_commission', 'institute_payout', 'status', 'paid_at', 'created_at',
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = [
        'transaction_id', 'booking__student__user__first_name',
        'booking__student__user__last_name',
    ]
    readonly_fields = [
        'transaction_id', 'platform_commission', 'institute_payout',
        'refund_amount', 'refund_reason', 'paid_at', 'refunded_at',
        'created_at', 'updated_at',
    ]
