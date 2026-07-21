from django.contrib import admin
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'registration_number', 'branch', 'vehicle_type', 'transmission',
        'brand', 'model_name', 'color', 'year_of_manufacture', 'is_available',
    ]
    list_filter = ['vehicle_type', 'transmission', 'is_available', 'branch']
    search_fields = ['registration_number', 'brand', 'model_name']
    readonly_fields = ['created_at', 'updated_at']
