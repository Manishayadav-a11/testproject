from django.db import models
from decimal import Decimal


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'

    student = models.ForeignKey(
        'students.Student', on_delete=models.CASCADE, related_name='bookings'
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='bookings'
    )
    branch = models.ForeignKey(
        'branches.Branch', on_delete=models.CASCADE, related_name='bookings'
    )
    instructor = models.ForeignKey(
        'instructors.Instructor', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings'
    )
    booking_date = models.DateField()
    preferred_time_slot = models.CharField(max_length=50, blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    special_requests = models.TextField(blank=True, default='')
    cancellation_reason = models.TextField(blank=True, default='')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking #{self.id} - {self.student.user.get_full_name()} - {self.course.name}"

    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.course.effective_price
        if not self.final_amount:
            self.final_amount = self.total_amount - self.discount_amount
        super().save(*args, **kwargs)
