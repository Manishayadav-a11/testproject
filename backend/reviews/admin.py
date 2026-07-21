from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'student', 'booking', 'institute', 'instructor',
        'course', 'rating', 'is_active', 'created_at',
    ]
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = [
        'student__user__first_name', 'student__user__last_name',
        'comment',
    ]
    readonly_fields = ['created_at', 'updated_at']
