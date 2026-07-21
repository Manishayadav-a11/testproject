from django.db import models
from decimal import Decimal


class Course(models.Model):
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

    class LearningLevel(models.TextChoices):
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'

    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE, related_name='courses'
    )
    instructor = models.ForeignKey(
        'instructors.Instructor', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses'
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField(blank=True, default='')
    duration_days = models.PositiveIntegerField(help_text='Duration in days')
    number_of_lessons = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    vehicle_type = models.CharField(
        max_length=20, choices=VehicleType.choices, default=VehicleType.CAR
    )
    transmission_type = models.CharField(
        max_length=20, choices=TransmissionType.choices, default=TransmissionType.MANUAL
    )
    learning_level = models.CharField(
        max_length=20, choices=LearningLevel.choices, default=LearningLevel.BEGINNER
    )
    includes = models.JSONField(default=list, blank=True, help_text='List of inclusions')
    is_active = models.BooleanField(default=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))
    total_reviews = models.PositiveIntegerField(default=0)
    total_bookings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['price']
        unique_together = ['branch', 'slug']

    def __str__(self):
        return f"{self.name} - {self.branch.institute.name}"

    @property
    def effective_price(self):
        if self.discounted_price and self.discounted_price < self.price:
            return self.discounted_price
        return self.price

    @property
    def discount_percentage(self):
        if self.discounted_price and self.discounted_price < self.price:
            discount = ((self.price - self.discounted_price) / self.price) * 100
            return round(discount, 1)
        return 0
