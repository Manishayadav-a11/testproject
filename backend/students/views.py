from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Student
from common.permissions import IsAdmin, IsStudentOrAdmin


def student_to_dict(s):
    return {
        'id': s.id,
        'user': {
            'id': s.user.id,
            'email': s.user.email,
            'first_name': s.user.first_name,
            'last_name': s.user.last_name,
            'phone': s.user.phone,
            'role': s.user.role,
            'profile_image': s.user.profile_image.url if s.user.profile_image else None,
            'city': s.user.city,
            'state': s.user.state,
        },
        'date_of_birth': str(s.date_of_birth) if s.date_of_birth else None,
        'learner_license_number': s.learner_license_number,
        'emergency_contact_name': s.emergency_contact_name,
        'emergency_contact_phone': s.emergency_contact_phone,
        'created_at': s.created_at.isoformat() if s.created_at else None,
        'updated_at': s.updated_at.isoformat() if s.updated_at else None,
    }


class StudentListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        qs = Student.objects.select_related('user').all()
        data = [student_to_dict(s) for s in qs]
        return Response(data)


class StudentDetailView(APIView):
    def get(self, request, id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            student = Student.objects.select_related('user').get(pk=id)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != 'admin' and student.user != request.user:
            return Response({'error': 'You do not have permission to view this student.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(student_to_dict(student))


class StudentProfileView(APIView):
    permission_classes = [IsStudentOrAdmin]

    def _get_student(self, request):
        id = request.query_params.get('id')
        if id:
            if request.user.role != 'admin':
                return None, Response({'error': 'Only admins can view other student profiles.'}, status=status.HTTP_403_FORBIDDEN)
            try:
                student = Student.objects.select_related('user').get(pk=id)
            except Student.DoesNotExist:
                return None, Response({'error': 'Student not found.'}, status=status.HTTP_404_NOT_FOUND)
            return student, None
        student, _ = Student.objects.select_related('user').get_or_create(user=request.user)
        return student, None

    def get(self, request):
        student, error = self._get_student(request)
        if error:
            return error
        return Response(student_to_dict(student))

    def _update(self, request):
        student, error = self._get_student(request)
        if error:
            return error
        data = request.data
        if request.method == 'PUT':
            required_fields = ['date_of_birth', 'learner_license_number', 'emergency_contact_name', 'emergency_contact_phone']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response({'error': f'The following fields are required: {", ".join(missing)}.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'date_of_birth' in data:
            student.date_of_birth = data['date_of_birth'] if data['date_of_birth'] else None
        if 'learner_license_number' in data:
            student.learner_license_number = data['learner_license_number']
        if 'emergency_contact_name' in data:
            student.emergency_contact_name = data['emergency_contact_name']
        if 'emergency_contact_phone' in data:
            student.emergency_contact_phone = data['emergency_contact_phone']
        student.save()
        return Response(student_to_dict(student))

    def put(self, request):
        return self._update(request)

    def patch(self, request):
        return self._update(request)
