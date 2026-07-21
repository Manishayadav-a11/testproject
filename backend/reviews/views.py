from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Review
from bookings.models import Booking
from students.models import Student
from common.permissions import IsAdmin, IsStudentOrAdmin, IsStudent


def review_to_dict(r):
    return {
        'id': r.id,
        'booking': r.booking_id,
        'student': {
            'id': r.student.id,
            'name': r.student.user.get_full_name(),
        },
        'institute': r.institute_id,
        'instructor': r.instructor_id,
        'course': r.course_id,
        'rating': r.rating,
        'comment': r.comment,
        'institute_rating': r.institute_rating,
        'instructor_rating': r.instructor_rating,
        'course_rating': r.course_rating,
        'is_active': r.is_active,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'updated_at': r.updated_at.isoformat() if r.updated_at else None,
    }


class ReviewListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        reviews = Review.objects.filter(is_active=True).select_related('student__user')
        institute_id = request.query_params.get('institute_id')
        instructor_id = request.query_params.get('instructor_id')
        course_id = request.query_params.get('course_id')
        if institute_id:
            reviews = reviews.filter(institute_id=institute_id)
        if instructor_id:
            reviews = reviews.filter(instructor_id=instructor_id)
        if course_id:
            reviews = reviews.filter(course_id=course_id)
        data = [review_to_dict(r) for r in reviews]
        return Response(data, status=status.HTTP_200_OK)


class ReviewCreateView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        data = request.data
        booking_id = data.get('booking')
        rating = data.get('rating')
        comment = data.get('comment', '')
        institute_rating = data.get('institute_rating')
        instructor_rating = data.get('instructor_rating')
        course_rating = data.get('course_rating')

        errors = {}
        if not booking_id:
            errors['booking'] = 'This field is required.'
        if rating is None:
            errors['rating'] = 'This field is required.'
        else:
            try:
                rating = int(rating)
            except (ValueError, TypeError):
                errors['rating'] = 'Invalid integer value.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        if not 1 <= rating <= 5:
            return Response({'rating': 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        for field_name, field_val in [('institute_rating', institute_rating), ('instructor_rating', instructor_rating), ('course_rating', course_rating)]:
            if field_val is not None:
                try:
                    val = int(field_val)
                except (ValueError, TypeError):
                    return Response({field_name: 'Invalid integer value.'}, status=status.HTTP_400_BAD_REQUEST)
                if not 1 <= val <= 5:
                    return Response({field_name: 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.select_related('student__user', 'course__branch__institute').get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'booking': 'Booking not found.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'detail': 'Student profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.student != student:
            return Response({'booking': 'You can only review your own bookings.'}, status=status.HTTP_400_BAD_REQUEST)

        if booking.status != Booking.Status.COMPLETED:
            return Response({'booking': 'You can only review completed bookings.'}, status=status.HTTP_400_BAD_REQUEST)

        if Review.objects.filter(booking=booking, student=student).exists():
            return Response({'booking': 'A review for this booking already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        institute = booking.course.branch.institute

        review = Review(
            booking=booking,
            student=student,
            institute=institute,
            rating=rating,
            comment=comment,
            institute_rating=institute_rating,
            instructor_rating=instructor_rating,
            course_rating=course_rating,
        )
        if not data.get('instructor'):
            review.instructor = booking.instructor
        if not data.get('course'):
            review.course = booking.course
        review.save()

        return Response(review_to_dict(review), status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            review = Review.objects.select_related('student__user').get(pk=id)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(review_to_dict(review), status=status.HTTP_200_OK)


class ReviewUpdateView(APIView):
    permission_classes = [IsStudent]

    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)

    def _update(self, request, id):
        try:
            review = Review.objects.select_related('student__user').get(pk=id)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response({'detail': 'You can only update your own reviews.'}, status=status.HTTP_403_FORBIDDEN)

        if review.student != student:
            return Response({'detail': 'You can only update your own reviews.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        for field in ('rating', 'comment', 'institute_rating', 'instructor_rating', 'course_rating'):
            if field in data:
                setattr(review, field, data[field])

        if 'rating' in data:
            try:
                r = int(data['rating'])
                if not 1 <= r <= 5:
                    return Response({'rating': 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)
                review.rating = r
            except (ValueError, TypeError):
                return Response({'rating': 'Invalid integer value.'}, status=status.HTTP_400_BAD_REQUEST)

        for field_name in ('institute_rating', 'instructor_rating', 'course_rating'):
            val = data.get(field_name)
            if val is not None:
                try:
                    v = int(val)
                except (ValueError, TypeError):
                    return Response({field_name: 'Invalid integer value.'}, status=status.HTTP_400_BAD_REQUEST)
                if not 1 <= v <= 5:
                    return Response({field_name: 'Rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        review.save()
        return Response(review_to_dict(review), status=status.HTTP_200_OK)


class ReviewDeleteView(APIView):
    permission_classes = [IsStudentOrAdmin]

    def delete(self, request, id):
        try:
            review = Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return Response({'detail': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You can only delete your own reviews.'}, status=status.HTTP_403_FORBIDDEN)
            if review.student != student:
                return Response({'detail': 'You can only delete your own reviews.'}, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyReviewsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        reviews = Review.objects.filter(student=student).select_related('student__user')
        data = [review_to_dict(r) for r in reviews]
        return Response(data, status=status.HTTP_200_OK)


class InstituteReviewsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, institute_id):
        reviews = Review.objects.filter(
            institute_id=institute_id, is_active=True
        ).select_related('student__user')
        data = [review_to_dict(r) for r in reviews]
        return Response(data, status=status.HTTP_200_OK)


class InstructorReviewsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, instructor_id):
        reviews = Review.objects.filter(
            instructor_id=instructor_id, is_active=True
        ).select_related('student__user')
        data = [review_to_dict(r) for r in reviews]
        return Response(data, status=status.HTTP_200_OK)


class CourseReviewsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, course_id):
        reviews = Review.objects.filter(
            course_id=course_id, is_active=True
        ).select_related('student__user')
        data = [review_to_dict(r) for r in reviews]
        return Response(data, status=status.HTTP_200_OK)
