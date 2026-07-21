from django.db import models


class Review(models.Model):
    booking = models.ForeignKey(
        'bookings.Booking', on_delete=models.CASCADE, related_name='reviews'
    )
    student = models.ForeignKey(
        'students.Student', on_delete=models.CASCADE, related_name='reviews'
    )
    institute = models.ForeignKey(
        'institutes.Institute', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True
    )
    instructor = models.ForeignKey(
        'instructors.Instructor', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True
    )
    course = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, default='')
    institute_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    instructor_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    course_rating = models.PositiveSmallIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review #{self.id} - {self.rating} stars"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_average_ratings()

    def _update_average_ratings(self):
        if self.institute:
            reviews = Review.objects.filter(institute=self.institute, is_active=True)
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.institute.average_rating = round(avg or 0, 2)
            self.institute.total_reviews = reviews.count()
            self.institute.save(update_fields=['average_rating', 'total_reviews'])

        if self.instructor:
            reviews = Review.objects.filter(instructor=self.instructor, is_active=True)
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.instructor.average_rating = round(avg or 0, 2)
            self.instructor.total_reviews = reviews.count()
            self.instructor.save(update_fields=['average_rating', 'total_reviews'])

        if self.course:
            reviews = Review.objects.filter(course=self.course, is_active=True)
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.course.average_rating = round(avg or 0, 2)
            self.course.total_reviews = reviews.count()
            self.course.save(update_fields=['average_rating', 'total_reviews'])
