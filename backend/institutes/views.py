from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.text import slugify
from django.db.models import Q
from .models import Institute
from common.permissions import IsAdmin, IsAdminOrReadOnly, IsInstituteOwnerOrAdmin


def institute_to_dict(inst, detail=False):
    first_branch = inst.branches.first() if hasattr(inst, 'branches') else None
    city = first_branch.city.name if first_branch and first_branch.city else ''
    state = first_branch.city.state.name if first_branch and first_branch.city and hasattr(first_branch.city, 'state') else ''
    d = {
        'id': inst.id,
        'name': inst.name,
        'slug': inst.slug,
        'logo': inst.logo.url if inst.logo else None,
        'contact_phone': inst.contact_phone,
        'status': inst.status,
        'is_approved': inst.status == Institute.Status.APPROVED,
        'city': city,
        'state': state,
        'average_rating': float(inst.average_rating),
        'total_reviews': inst.total_reviews,
        'review_count': inst.total_reviews,
        'is_featured': inst.is_featured,
        'created_at': inst.created_at.isoformat() if inst.created_at else None,
    }
    if detail:
        d.update({
            'owner': inst.owner_id,
            'owner_email': inst.owner.email,
            'category': inst.category_id,
            'category_name': inst.category.name if inst.category else None,
            'description': inst.description,
            'contact_email': inst.contact_email,
            'website': inst.website,
            'license_number': inst.license_number,
            'license_document': inst.license_document.url if inst.license_document else None,
            'commission_rate': float(inst.commission_rate),
            'updated_at': inst.updated_at.isoformat() if inst.updated_at else None,
        })
    return d


class InstituteListView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        user = request.user
        queryset = Institute.objects.select_related('owner', 'category').all()
        if user.is_authenticated and user.role == 'admin':
            pass
        elif user.is_authenticated and user.role == 'institute_owner':
            queryset = queryset.filter(owner=user)
        else:
            queryset = queryset.filter(status=Institute.Status.APPROVED)
        search = request.query_params.get('search')
        category = request.query_params.get('category')
        is_featured = request.query_params.get('is_featured')
        ordering = request.query_params.get('ordering', '-created_at')
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            queryset = queryset.filter(category_id=category)
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() in ('true', '1'))
        allowed_orderings = ['name', '-name', 'created_at', '-created_at', 'average_rating', '-average_rating']
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')
        return Response([institute_to_dict(i) for i in queryset])


class InstituteCreateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def post(self, request):
        user = request.user
        name = request.data.get('name', '').strip()
        contact_phone = request.data.get('contact_phone', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not contact_phone:
            return Response({'error': 'Contact phone is required.'}, status=status.HTTP_400_BAD_REQUEST)
        slug = slugify(name)
        if Institute.objects.filter(slug=slug).exists():
            base_slug = slug
            counter = 1
            while Institute.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
        category_id = request.data.get('category')
        category_obj = None
        if category_id:
            from common.models import Category as CategoryModel
            try:
                category_obj = CategoryModel.objects.get(id=category_id)
            except CategoryModel.DoesNotExist:
                return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        institute = Institute.objects.create(
            owner=user,
            category=category_obj,
            name=name,
            slug=slug,
            logo=request.FILES.get('logo'),
            description=request.data.get('description', ''),
            contact_email=request.data.get('contact_email', ''),
            contact_phone=contact_phone,
            website=request.data.get('website', ''),
            license_number=request.data.get('license_number', ''),
            license_document=request.FILES.get('license_document'),
            commission_rate=request.data.get('commission_rate', 10.00),
        )
        return Response(institute_to_dict(institute, detail=True), status=status.HTTP_201_CREATED)


class InstituteMineView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def get(self, request):
        user = request.user
        if not user.is_authenticated or user.role != 'institute_owner':
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        queryset = Institute.objects.select_related('owner', 'category').filter(owner=user).order_by('-created_at')
        return Response([institute_to_dict(i) for i in queryset])


class InstituteFeaturedView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Institute.objects.select_related('owner', 'category').filter(
            status=Institute.Status.APPROVED, is_featured=True
        ).order_by('-created_at')
        return Response([institute_to_dict(i) for i in queryset])


class InstituteSearchView(APIView):
    permission_classes = []

    def get(self, request):
        queryset = Institute.objects.select_related('owner', 'category').filter(
            status=Institute.Status.APPROVED
        ).distinct()
        q = request.query_params.get('q')
        city = request.query_params.get('city')
        category = request.query_params.get('category')
        min_rating = request.query_params.get('min_rating')
        ordering = request.query_params.get('ordering', '-average_rating')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q) | Q(branches__city__name__icontains=q)
            ).distinct()
        if city:
            queryset = queryset.filter(branches__city_id=city).distinct()
        if category:
            queryset = queryset.filter(category_id=category)
        if min_rating:
            queryset = queryset.filter(average_rating__gte=min_rating)
        allowed_orderings = ['name', '-name', 'average_rating', '-average_rating', 'created_at', '-created_at']
        if ordering in allowed_orderings:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-average_rating')
        return Response([institute_to_dict(i) for i in queryset])


class InstituteDetailView(APIView):
    permission_classes = []

    def get(self, request, id):
        user = request.user
        try:
            institute = Institute.objects.select_related('owner', 'category').prefetch_related('branches').get(pk=id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        if institute.status != Institute.Status.APPROVED:
            if not user.is_authenticated:
                return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
            if user.role == 'admin':
                pass
            elif user.role == 'institute_owner' and institute.owner == user:
                pass
            else:
                return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(institute_to_dict(institute, detail=True))


class InstituteUpdateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def put(self, request, id):
        user = request.user
        try:
            institute = Institute.objects.select_related('owner', 'category').prefetch_related('branches').get(pk=id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role != 'admin' and institute.owner != user:
            return Response({'error': 'You do not own this institute.'}, status=status.HTTP_403_FORBIDDEN)
        name = request.data.get('name', '').strip()
        contact_phone = request.data.get('contact_phone', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not contact_phone:
            return Response({'error': 'Contact phone is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if name != institute.name:
            slug = slugify(name)
            if Institute.objects.filter(slug=slug).exclude(pk=id).exists():
                base_slug = slug
                counter = 1
                while Institute.objects.filter(slug=slug).exclude(pk=id).exists():
                    slug = f'{base_slug}-{counter}'
                    counter += 1
            institute.slug = slug
        if 'logo' in request.FILES:
            institute.logo = request.FILES['logo']
        if 'license_document' in request.FILES:
            institute.license_document = request.FILES['license_document']
        category_id = request.data.get('category')
        category_obj = institute.category
        if category_id != institute.category_id:
            from common.models import Category as CategoryModel
            if category_id:
                try:
                    category_obj = CategoryModel.objects.get(id=category_id)
                except CategoryModel.DoesNotExist:
                    return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                category_obj = None
        institute.name = name
        institute.contact_phone = contact_phone
        institute.description = request.data.get('description', institute.description)
        institute.contact_email = request.data.get('contact_email', institute.contact_email)
        institute.website = request.data.get('website', institute.website)
        institute.license_number = request.data.get('license_number', institute.license_number)
        institute.is_featured = bool(request.data.get('is_featured', institute.is_featured))
        institute.commission_rate = request.data.get('commission_rate', institute.commission_rate)
        institute.category = category_obj
        institute.save()
        return Response(institute_to_dict(institute, detail=True))

    def patch(self, request, id):
        user = request.user
        try:
            institute = Institute.objects.select_related('owner', 'category').prefetch_related('branches').get(pk=id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role != 'admin' and institute.owner != user:
            return Response({'error': 'You do not own this institute.'}, status=status.HTTP_403_FORBIDDEN)
        if 'name' in request.data:
            new_name = request.data['name'].strip()
            if new_name and new_name != institute.name:
                slug = slugify(new_name)
                if Institute.objects.filter(slug=slug).exclude(pk=id).exists():
                    base_slug = slug
                    counter = 1
                    while Institute.objects.filter(slug=slug).exclude(pk=id).exists():
                        slug = f'{base_slug}-{counter}'
                        counter += 1
                institute.slug = slug
            institute.name = new_name
        if 'contact_phone' in request.data:
            institute.contact_phone = request.data['contact_phone']
        if 'description' in request.data:
            institute.description = request.data['description']
        if 'contact_email' in request.data:
            institute.contact_email = request.data['contact_email']
        if 'website' in request.data:
            institute.website = request.data['website']
        if 'license_number' in request.data:
            institute.license_number = request.data['license_number']
        if 'is_featured' in request.data:
            institute.is_featured = bool(request.data['is_featured'])
        if 'commission_rate' in request.data:
            institute.commission_rate = request.data['commission_rate']
        if 'category' in request.data:
            from common.models import Category as CategoryModel
            cat_id = request.data['category']
            if cat_id:
                try:
                    institute.category = CategoryModel.objects.get(id=cat_id)
                except CategoryModel.DoesNotExist:
                    return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                institute.category = None
        if 'logo' in request.FILES:
            institute.logo = request.FILES['logo']
        if 'license_document' in request.FILES:
            institute.license_document = request.FILES['license_document']
        institute.save()
        return Response(institute_to_dict(institute, detail=True))


class InstituteDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            institute = Institute.objects.get(pk=id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        institute.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstituteApproveView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id):
        try:
            institute = Institute.objects.select_related('owner', 'category').prefetch_related('branches').get(pk=id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        new_status = request.data.get('status', '').strip()
        allowed = [Institute.Status.APPROVED, Institute.Status.REJECTED, Institute.Status.SUSPENDED]
        if new_status not in allowed:
            return Response({'error': 'Status must be approved, rejected, or suspended.'}, status=status.HTTP_400_BAD_REQUEST)
        institute.status = new_status
        institute.save()
        return Response(institute_to_dict(institute, detail=True))
