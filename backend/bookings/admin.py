from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'student', 'course', 'branch', 'instructor', 'status',
        'booking_date', 'final_amount', 'created_at',
    ]
    list_filter = ['status', 'booking_date', 'created_at']
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'student__user__email', 'course__name',
    ]
    readonly_fields = [
        'total_amount', 'discount_amount', 'final_amount',
        'cancelled_at', 'completed_at', 'created_at', 'updated_at',
    ]
