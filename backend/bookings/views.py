from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Booking
from courses.models import Course
from branches.models import Branch
from students.models import Student
from common.permissions import IsAdmin, IsStudentOrAdmin, IsInstituteOwnerOrAdmin, IsStudent


def booking_to_dict(b, detail=False):
    d = {
        'id': b.id,
        'student': {
            'id': b.student.id,
            'user': {
                'id': b.student.user.id,
                'first_name': b.student.user.first_name,
                'last_name': b.student.user.last_name,
                'email': b.student.user.email,
                'phone': b.student.user.phone,
            }
        } if detail else b.student_id,
        'course': {
            'id': b.course.id,
            'name': b.course.name,
            'price': float(b.course.price),
        } if detail else b.course_id,
        'branch': b.branch_id,
        'branch_name': b.branch.name,
        'instructor': b.instructor_id,
        'instructor_name': (b.instructor.user.get_full_name() if b.instructor else None) if detail else None,
        'booking_date': str(b.booking_date) if b.booking_date else None,
        'preferred_time_slot': b.preferred_time_slot,
        'status': b.status,
        'total_amount': float(b.total_amount),
        'discount_amount': float(b.discount_amount),
        'final_amount': float(b.final_amount),
        'created_at': b.created_at.isoformat() if b.created_at else None,
    }
    if detail:
        d.update({
            'special_requests': b.special_requests,
            'cancellation_reason': b.cancellation_reason,
            'cancelled_at': b.cancelled_at.isoformat() if b.cancelled_at else None,
            'completed_at': b.completed_at.isoformat() if b.completed_at else None,
            'updated_at': b.updated_at.isoformat() if b.updated_at else None,
        })
    return d


class BookingListView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        if user.role == 'admin':
            bookings = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).all()
        elif user.role == 'institute_owner':
            bookings = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).filter(course__branch__institute__owner=user)
        elif user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)
            bookings = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).filter(student=student)
        else:
            return Response([], status=status.HTTP_200_OK)

        data = [booking_to_dict(b) for b in bookings]
        return Response(data, status=status.HTTP_200_OK)


class BookingCreateView(APIView):
    permission_classes = [IsStudent]

    def post(self, request):
        data = request.data
        course_id = data.get('course')
        branch_id = data.get('branch')
        booking_date = data.get('booking_date')
        preferred_time_slot = data.get('preferred_time_slot', '')
        instructor_id = data.get('instructor')
        special_requests = data.get('special_requests', '')

        errors = {}
        if not course_id:
            errors['course'] = 'This field is required.'
        if not branch_id:
            errors['branch'] = 'This field is required.'
        if not booking_date:
            errors['booking_date'] = 'This field is required.'
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'course': 'Course not found.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'branch': 'Branch not found.'}, status=status.HTTP_400_BAD_REQUEST)

        if not course.is_active:
            return Response({'course': 'This course is not available.'}, status=status.HTTP_400_BAD_REQUEST)
        if not branch.is_active:
            return Response({'branch': 'This branch is not active.'}, status=status.HTTP_400_BAD_REQUEST)
        if course.branch_id != branch.id:
            return Response({'branch': 'This branch does not offer the selected course.'}, status=status.HTTP_400_BAD_REQUEST)

        from datetime import date as date_type
        try:
            bd = date_type.fromisoformat(booking_date)
        except (ValueError, TypeError):
            return Response({'booking_date': 'Invalid date format.'}, status=status.HTTP_400_BAD_REQUEST)

        if bd < timezone.now().date():
            return Response({'booking_date': 'Booking date cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            student = Student.objects.create(user=request.user)

        instructor = None
        if instructor_id:
            from instructors.models import Instructor
            try:
                instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return Response({'instructor': 'Instructor not found.'}, status=status.HTTP_400_BAD_REQUEST)

        booking = Booking(
            student=student,
            course=course,
            branch=branch,
            instructor=instructor,
            booking_date=bd,
            preferred_time_slot=preferred_time_slot,
            special_requests=special_requests,
        )
        booking.total_amount = course.effective_price
        booking.final_amount = booking.total_amount - booking.discount_amount
        booking.save()

        return Response(booking_to_dict(booking, detail=True), status=status.HTTP_201_CREATED)


class BookingDetailView(APIView):
    def get(self, request, id):
        try:
            booking = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).get(pk=id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role == 'admin':
            pass
        elif user.role == 'institute_owner':
            if booking.course.branch.institute.owner != user:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        elif user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
            if booking.student != student:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(booking_to_dict(booking, detail=True), status=status.HTTP_200_OK)


class BookingUpdateView(APIView):
    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)

    def _update(self, request, id):
        try:
            booking = Booking.objects.select_related(
                'student__user', 'course__branch__institute', 'branch', 'instructor__user'
            ).get(pk=id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        data = request.data

        if user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
            if booking.student != student:
                return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
            if booking.status not in ('pending',):
                return Response(
                    {'detail': f"Cannot update a booking with status '{booking.status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            allowed_fields = {'preferred_time_slot', 'special_requests', 'booking_date'}
            for field in allowed_fields:
                if field in data:
                    setattr(booking, field, data[field])
            if 'booking_date' in data:
                from datetime import date as date_type
                try:
                    bd = date_type.fromisoformat(data['booking_date'])
                    if bd < timezone.now().date():
                        return Response({'booking_date': 'Booking date cannot be in the past.'}, status=status.HTTP_400_BAD_REQUEST)
                    booking.booking_date = bd
                except (ValueError, TypeError):
                    return Response({'booking_date': 'Invalid date format.'}, status=status.HTTP_400_BAD_REQUEST)
            booking.save()
        elif user.role in ('admin', 'institute_owner'):
            if user.role == 'institute_owner':
                if booking.course.branch.institute.owner != user:
                    return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
            new_status = data.get('status')
            if new_status:
                allowed_transitions = {
                    'pending': ['confirmed', 'cancelled'],
                    'confirmed': ['in_progress', 'cancelled'],
                    'in_progress': ['completed'],
                }
                current = booking.status
                if current in allowed_transitions and new_status not in allowed_transitions[current]:
                    return Response(
                        {'detail': f"Cannot change status from '{current}' to '{new_status}'."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                booking.status = new_status
                if new_status == 'completed':
                    booking.completed_at = timezone.now()
                if new_status == 'cancelled':
                    booking.cancelled_at = timezone.now()
                booking.save()
        else:
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

        return Response(booking_to_dict(booking, detail=True), status=status.HTTP_200_OK)


class BookingConfirmView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def post(self, request, id):
        try:
            booking = Booking.objects.select_related(
                'student__user', 'course__branch__institute', 'branch', 'instructor__user'
            ).get(pk=id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.role != 'admin':
            institute = booking.course.branch.institute
            if institute.owner != user:
                return Response({'detail': 'You do not have permission to confirm this booking.'}, status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'pending':
            return Response(
                {'detail': f"Cannot confirm a booking with status '{booking.status}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=['status', 'updated_at'])

        return Response(booking_to_dict(booking, detail=True), status=status.HTTP_200_OK)


class BookingCancelView(APIView):
    permission_classes = [IsStudentOrAdmin]

    def post(self, request, id):
        try:
            booking = Booking.objects.select_related(
                'student__user', 'course__branch__institute', 'branch', 'instructor__user'
            ).get(pk=id)
        except Booking.DoesNotExist:
            return Response({'detail': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        cancellation_reason = request.data.get('cancellation_reason', '')

        if user.role == 'student':
            try:
                student = user.student_profile
            except Student.DoesNotExist:
                return Response({'detail': 'You can only cancel your own bookings.'}, status=status.HTTP_403_FORBIDDEN)
            if booking.student != student:
                return Response({'detail': 'You can only cancel your own bookings.'}, status=status.HTTP_403_FORBIDDEN)
            if booking.status not in ('pending', 'confirmed'):
                return Response(
                    {'detail': f"Cannot cancel a booking with status '{booking.status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif user.role == 'admin':
            if booking.status in ('completed', 'cancelled', 'refunded'):
                return Response(
                    {'detail': f"Cannot cancel a booking with status '{booking.status}'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response({'detail': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)

        booking.status = Booking.Status.CANCELLED
        booking.cancellation_reason = cancellation_reason
        booking.cancelled_at = timezone.now()
        booking.save(update_fields=['status', 'cancellation_reason', 'cancelled_at', 'updated_at'])

        return Response(booking_to_dict(booking, detail=True), status=status.HTTP_200_OK)


class StudentBookingsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        try:
            student = request.user.student_profile
        except Student.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        bookings = Booking.objects.select_related(
            'student__user', 'course', 'branch', 'instructor__user'
        ).filter(student=student)
        data = [booking_to_dict(b) for b in bookings]
        return Response(data, status=status.HTTP_200_OK)


class InstituteBookingsView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def get(self, request, institute_id):
        user = request.user
        if user.role == 'admin':
            bookings = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).filter(course__branch__institute_id=institute_id)
        else:
            bookings = Booking.objects.select_related(
                'student__user', 'course', 'branch', 'instructor__user'
            ).filter(
                course__branch__institute__owner=user,
                course__branch__institute_id=institute_id,
            )
        data = [booking_to_dict(b) for b in bookings]
        return Response(data, status=status.HTTP_200_OK)
