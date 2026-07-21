from django.contrib import admin
from .models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'slug', 'branch', 'instructor', 'price', 'discounted_price',
        'vehicle_type', 'transmission_type', 'learning_level', 'is_active',
        'average_rating', 'total_bookings', 'created_at',
    ]
    list_filter = ['vehicle_type', 'transmission_type', 'learning_level', 'is_active', 'branch']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['average_rating', 'total_reviews', 'total_bookings', 'created_at', 'updated_at']
