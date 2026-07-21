from django.db import models


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'car', 'Car'
        BIKE = 'bike', 'Bike'
        SUV = 'suv', 'SUV'
        TRUCK = 'truck', 'Truck'
        BUS = 'bus', 'Bus'
        OTHER = 'other', 'Other'

    class TransmissionType(models.TextChoices):
        MANUAL = 'manual', 'Manual'
        AUTOMATIC = 'automatic', 'Automatic'

    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE, related_name='vehicles'
    )
    registration_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VehicleType.choices, default=VehicleType.CAR)
    transmission = models.CharField(
        max_length=20, choices=TransmissionType.choices, default=TransmissionType.MANUAL
    )
    brand = models.CharField(max_length=100, blank=True, default='')
    model_name = models.CharField(max_length=100, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')
    year_of_manufacture = models.PositiveIntegerField(null=True, blank=True)
    insurance_valid_upto = models.DateField(null=True, blank=True)
    fitness_certificate_valid_upto = models.DateField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        return f"{self.brand} {self.model_name} ({self.registration_number})"
