from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.utils.text import slugify
from decimal import Decimal
from .models import Course
from branches.models import Branch
from common.permissions import IsAdmin, IsInstituteOwnerOrAdmin


def course_to_dict(c, detail=False):
    d = {
        'id': c.id,
        'name': c.name,
        'slug': c.slug,
        'branch': c.branch_id,
        'branch_name': c.branch.name,
        'institute_name': c.branch.institute.name,
        'price': float(c.price),
        'discounted_price': float(c.discounted_price) if c.discounted_price else None,
        'effective_price': float(c.effective_price),
        'discount_percentage': c.discount_percentage,
        'vehicle_type': c.vehicle_type,
        'transmission_type': c.transmission_type,
        'learning_level': c.learning_level,
        'duration_days': c.duration_days,
        'number_of_lessons': c.number_of_lessons,
        'is_active': c.is_active,
        'average_rating': float(c.average_rating),
        'total_reviews': c.total_reviews,
        'total_bookings': c.total_bookings,
        'created_at': c.created_at.isoformat() if c.created_at else None,
    }
    if detail:
        d.update({
            'description': c.description,
            'instructor': c.instructor_id,
            'instructor_name': c.instructor.user.get_full_name() if c.instructor else None,
            'includes': c.includes,
            'updated_at': c.updated_at.isoformat() if c.updated_at else None,
        })
    return d


class CourseListCreateView(APIView):
    def get(self, request):
        qs = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').filter(is_active=True)
        branch = request.query_params.get('branch')
        if branch:
            qs = qs.filter(branch_id=branch)
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        transmission_type = request.query_params.get('transmission')
        if transmission_type:
            qs = qs.filter(transmission_type=transmission_type)
        learning_level = request.query_params.get('learning_level')
        if learning_level:
            qs = qs.filter(learning_level=learning_level)
        price_min = request.query_params.get('min_price')
        if price_min:
            qs = qs.filter(price__gte=Decimal(price_min))
        price_max = request.query_params.get('max_price')
        if price_max:
            qs = qs.filter(price__lte=Decimal(price_max))
        data = [course_to_dict(c) for c in qs]
        return Response(data)

    permission_classes = [IsInstituteOwnerOrAdmin]

    def post(self, request):
        data = request.data
        branch_id = data.get('branch_id')
        name = data.get('name')
        if not branch_id:
            return Response({'error': 'branch_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not name:
            return Response({'error': 'name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != 'admin':
            if not hasattr(branch.institute, 'owner') or branch.institute.owner != request.user:
                return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        duration_days = data.get('duration_days')
        price = data.get('price')
        if duration_days is None:
            return Response({'error': 'duration_days is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if price is None:
            return Response({'error': 'price is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(duration_days, int) or duration_days < 1:
            return Response({'error': 'duration_days must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            price = Decimal(str(price))
        except Exception:
            return Response({'error': 'price must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
        discounted_price = data.get('discounted_price')
        if discounted_price is not None:
            try:
                discounted_price = Decimal(str(discounted_price))
            except Exception:
                return Response({'error': 'discounted_price must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
        vehicle_type_val = data.get('vehicle_type', 'car')
        transmission_type_val = data.get('transmission_type', 'manual')
        learning_level_val = data.get('learning_level', 'beginner')
        if vehicle_type_val not in dict(Course.VehicleType.choices):
            return Response({'error': f'vehicle_type must be one of: {", ".join(dict(Course.VehicleType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        if transmission_type_val not in dict(Course.TransmissionType.choices):
            return Response({'error': f'transmission_type must be one of: {", ".join(dict(Course.TransmissionType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        if learning_level_val not in dict(Course.LearningLevel.choices):
            return Response({'error': f'learning_level must be one of: {", ".join(dict(Course.LearningLevel.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        instructor_id = data.get('instructor_id')
        instructor = None
        if instructor_id:
            from instructors.models import Instructor
            try:
                instructor = Instructor.objects.get(id=instructor_id)
            except Instructor.DoesNotExist:
                return Response({'error': 'Instructor not found.'}, status=status.HTTP_404_NOT_FOUND)
        includes = data.get('includes', [])
        if not isinstance(includes, list):
            return Response({'error': 'includes must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
        slug = data.get('slug') or slugify(name)
        if Course.objects.filter(branch=branch, slug=slug).exists():
            base_slug = slug
            counter = 1
            while Course.objects.filter(branch=branch, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
        course = Course.objects.create(
            branch=branch,
            instructor=instructor,
            name=name,
            slug=slug,
            description=data.get('description', ''),
            duration_days=duration_days,
            number_of_lessons=data.get('number_of_lessons', 1),
            price=price,
            discounted_price=discounted_price,
            vehicle_type=vehicle_type_val,
            transmission_type=transmission_type_val,
            learning_level=learning_level_val,
            includes=includes,
            is_active=data.get('is_active', True),
        )
        return Response(course_to_dict(course, detail=True), status=status.HTTP_201_CREATED)


class CourseSearchView(APIView):
    def get(self, request):
        qs = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').filter(is_active=True)
        name = request.query_params.get('name')
        if name:
            qs = qs.filter(name__icontains=name)
        q = request.query_params.get('q')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        city = request.query_params.get('city')
        if city:
            qs = qs.filter(Q(branch__city__name__icontains=city) | Q(branch__address__icontains=city))
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        learning_level = request.query_params.get('learning_level')
        if learning_level:
            qs = qs.filter(learning_level=learning_level)
        price_min = request.query_params.get('min_price')
        if price_min:
            qs = qs.filter(price__gte=Decimal(price_min))
        price_max = request.query_params.get('max_price')
        if price_max:
            qs = qs.filter(price__lte=Decimal(price_max))
        data = [course_to_dict(c) for c in qs]
        return Response(data)


class PopularCoursesView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        qs = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').filter(is_active=True).order_by('-total_bookings')[:limit]
        data = [course_to_dict(c) for c in qs]
        return Response(data)


class CourseDetailView(APIView):
    def get(self, request, id):
        try:
            course = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').get(pk=id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(course_to_dict(course, detail=True))


class CourseUpdateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def _check_permission(self, request, course):
        if request.user.role == 'admin':
            return True
        return hasattr(course.branch.institute, 'owner') and course.branch.institute.owner == request.user

    def _update(self, request, id):
        try:
            course = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').get(pk=id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not self._check_permission(request, course):
            return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if request.method == 'PUT':
            required_fields = ['name', 'duration_days', 'price', 'vehicle_type', 'transmission_type', 'learning_level']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response({'error': f'The following fields are required: {", ".join(missing)}.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'name' in data:
            course.name = data['name']
            if 'slug' not in data:
                new_slug = slugify(data['name'])
                if new_slug != course.slug:
                    if Course.objects.filter(branch=course.branch, slug=new_slug).exclude(pk=id).exists():
                        base_slug = new_slug
                        counter = 1
                        while Course.objects.filter(branch=course.branch, slug=new_slug).exclude(pk=id).exists():
                            new_slug = f"{base_slug}-{counter}"
                            counter += 1
                    course.slug = new_slug
        if 'slug' in data:
            new_slug = data['slug']
            if Course.objects.filter(branch=course.branch, slug=new_slug).exclude(pk=id).exists():
                return Response({'error': 'A course with this slug already exists for this branch.'}, status=status.HTTP_400_BAD_REQUEST)
            course.slug = new_slug
        if 'description' in data:
            course.description = data['description']
        if 'duration_days' in data:
            if not isinstance(data['duration_days'], int) or data['duration_days'] < 1:
                return Response({'error': 'duration_days must be a positive integer.'}, status=status.HTTP_400_BAD_REQUEST)
            course.duration_days = data['duration_days']
        if 'number_of_lessons' in data:
            course.number_of_lessons = data['number_of_lessons']
        if 'price' in data:
            try:
                course.price = Decimal(str(data['price']))
            except Exception:
                return Response({'error': 'price must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'discounted_price' in data:
            if data['discounted_price'] is not None:
                try:
                    course.discounted_price = Decimal(str(data['discounted_price']))
                except Exception:
                    return Response({'error': 'discounted_price must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                course.discounted_price = None
        if 'vehicle_type' in data:
            if data['vehicle_type'] not in dict(Course.VehicleType.choices):
                return Response({'error': f'vehicle_type must be one of: {", ".join(dict(Course.VehicleType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
            course.vehicle_type = data['vehicle_type']
        if 'transmission_type' in data:
            if data['transmission_type'] not in dict(Course.TransmissionType.choices):
                return Response({'error': f'transmission_type must be one of: {", ".join(dict(Course.TransmissionType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
            course.transmission_type = data['transmission_type']
        if 'learning_level' in data:
            if data['learning_level'] not in dict(Course.LearningLevel.choices):
                return Response({'error': f'learning_level must be one of: {", ".join(dict(Course.LearningLevel.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
            course.learning_level = data['learning_level']
        if 'instructor_id' in data:
            if data['instructor_id'] is not None:
                from instructors.models import Instructor
                try:
                    instructor = Instructor.objects.get(id=data['instructor_id'])
                    course.instructor = instructor
                except Instructor.DoesNotExist:
                    return Response({'error': 'Instructor not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                course.instructor = None
        if 'includes' in data:
            if not isinstance(data['includes'], list):
                return Response({'error': 'includes must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
            course.includes = data['includes']
        if 'is_active' in data:
            course.is_active = bool(data['is_active'])
        course.save()
        return Response(course_to_dict(course, detail=True))

    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)


class CourseDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            course = Course.objects.get(pk=id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found.'}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BranchCoursesView(APIView):
    def get(self, request, branch_id):
        try:
            Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = Course.objects.select_related('branch', 'branch__institute', 'instructor', 'instructor__user').filter(branch_id=branch_id, is_active=True)
        data = [course_to_dict(c) for c in qs]
        return Response(data)
