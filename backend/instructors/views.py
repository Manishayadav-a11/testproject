from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Instructor
from branches.models import Branch
from common.permissions import IsAdmin, IsInstituteOwnerOrAdmin

User = get_user_model()


def instructor_to_dict(inst, detail=False):
    d = {
        'id': inst.id,
        'user': {
            'id': inst.user.id,
            'first_name': inst.user.first_name,
            'last_name': inst.user.last_name,
            'email': inst.user.email,
            'phone': inst.user.phone,
            'profile_image': inst.user.profile_image.url if inst.user.profile_image else None,
        },
        'branch': inst.branch_id,
        'branch_name': inst.branch.name,
        'experience_years': inst.experience_years,
        'languages': inst.languages,
        'is_available': inst.is_available,
        'home_pickup_available': inst.home_pickup_available,
        'female_instructor': inst.female_instructor,
        'average_rating': float(inst.average_rating),
        'total_reviews': inst.total_reviews,
        'created_at': inst.created_at.isoformat() if inst.created_at else None,
    }
    if detail:
        d.update({
            'license_number': inst.license_number,
            'bio': inst.bio,
            'updated_at': inst.updated_at.isoformat() if inst.updated_at else None,
        })
    return d


class InstructorListView(APIView):
    def get(self, request):
        qs = Instructor.objects.select_related('user', 'branch').all()
        branch = request.query_params.get('branch')
        if branch:
            qs = qs.filter(branch_id=branch)
        female_instructor = request.query_params.get('female_instructor')
        if female_instructor is not None:
            qs = qs.filter(female_instructor=female_instructor.lower() in ('true', '1'))
        is_available = request.query_params.get('is_available')
        if is_available is not None:
            qs = qs.filter(is_available=is_available.lower() in ('true', '1'))
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search)
            )
        data = [instructor_to_dict(i) for i in qs]
        return Response(data)


class InstructorCreateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        branch_id = data.get('branch_id')
        if not user_id:
            return Response({'error': 'user_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not branch_id:
            return Response({'error': 'branch_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != 'admin':
            if not hasattr(branch.institute, 'owner') or branch.institute.owner != request.user:
                return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        if Instructor.objects.filter(user=user).exists():
            return Response({'error': 'Instructor profile already exists for this user.'}, status=status.HTTP_400_BAD_REQUEST)
        experience_years = data.get('experience_years', 0)
        languages = data.get('languages', [])
        if not isinstance(experience_years, int) or experience_years < 0:
            return Response({'error': 'experience_years must be a non-negative integer.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(languages, list):
            return Response({'error': 'languages must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
        instructor = Instructor.objects.create(
            user=user,
            branch=branch,
            license_number=data.get('license_number', ''),
            experience_years=experience_years,
            languages=languages,
            bio=data.get('bio', ''),
            is_available=data.get('is_available', True),
            home_pickup_available=data.get('home_pickup_available', False),
            female_instructor=data.get('female_instructor', False),
        )
        return Response(instructor_to_dict(instructor, detail=True), status=status.HTTP_201_CREATED)


class InstructorDetailView(APIView):
    def get(self, request, id):
        try:
            inst = Instructor.objects.select_related('user', 'branch').get(pk=id)
        except Instructor.DoesNotExist:
            return Response({'error': 'Instructor not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(instructor_to_dict(inst, detail=True))


class InstructorUpdateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def _check_permission(self, request, instructor):
        if request.user.role == 'admin':
            return True
        return hasattr(instructor.branch.institute, 'owner') and instructor.branch.institute.owner == request.user

    def _update(self, request, id):
        try:
            inst = Instructor.objects.select_related('user', 'branch', 'branch__institute').get(pk=id)
        except Instructor.DoesNotExist:
            return Response({'error': 'Instructor not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not self._check_permission(request, inst):
            return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if request.method == 'PUT':
            required_fields = ['license_number', 'experience_years', 'languages', 'is_available', 'home_pickup_available', 'female_instructor']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response({'error': f'The following fields are required: {", ".join(missing)}.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'experience_years' in data:
            if not isinstance(data['experience_years'], int) or data['experience_years'] < 0:
                return Response({'error': 'experience_years must be a non-negative integer.'}, status=status.HTTP_400_BAD_REQUEST)
            inst.experience_years = data['experience_years']
        if 'languages' in data:
            if not isinstance(data['languages'], list):
                return Response({'error': 'languages must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
            inst.languages = data['languages']
        if 'license_number' in data:
            inst.license_number = data['license_number']
        if 'bio' in data:
            inst.bio = data['bio']
        if 'is_available' in data:
            inst.is_available = bool(data['is_available'])
        if 'home_pickup_available' in data:
            inst.home_pickup_available = bool(data['home_pickup_available'])
        if 'female_instructor' in data:
            inst.female_instructor = bool(data['female_instructor'])
        inst.save()
        return Response(instructor_to_dict(inst, detail=True))

    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)


class InstructorDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            inst = Instructor.objects.get(pk=id)
        except Instructor.DoesNotExist:
            return Response({'error': 'Instructor not found.'}, status=status.HTTP_404_NOT_FOUND)
        inst.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BranchInstructorsView(APIView):
    def get(self, request, branch_id):
        try:
            Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = Instructor.objects.select_related('user', 'branch').filter(branch_id=branch_id)
        data = [instructor_to_dict(i) for i in qs]
        return Response(data)


class AvailableInstructorsView(APIView):
    def get(self, request, branch_id):
        try:
            Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = Instructor.objects.select_related('user', 'branch').filter(branch_id=branch_id, is_available=True)
        female_only = request.query_params.get('female_only')
        if female_only and female_only.lower() == 'true':
            qs = qs.filter(female_instructor=True)
        languages = request.query_params.get('languages')
        if languages:
            for lang in languages.split(','):
                qs = qs.filter(languages__contains=[lang.strip()])
        data = [instructor_to_dict(i) for i in qs]
        return Response(data)
