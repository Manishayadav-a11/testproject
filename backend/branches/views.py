from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Branch
from institutes.models import Institute
from common.permissions import IsAdmin, IsAdminOrReadOnly, IsInstituteOwnerOrAdmin


def branch_to_dict(b):
    return {
        'id': b.id,
        'institute': b.institute_id,
        'institute_name': b.institute.name,
        'name': b.name,
        'address': b.address,
        'city': b.city_id,
        'city_name': b.city.name if b.city else None,
        'state': b.state_id,
        'state_name': b.state.name if b.state else None,
        'pincode': b.pincode,
        'contact_number': b.contact_number,
        'latitude': str(b.latitude) if b.latitude else None,
        'longitude': str(b.longitude) if b.longitude else None,
        'monday_open': str(b.monday_open) if b.monday_open else None,
        'monday_close': str(b.monday_close) if b.monday_close else None,
        'tuesday_open': str(b.tuesday_open) if b.tuesday_open else None,
        'tuesday_close': str(b.tuesday_close) if b.tuesday_close else None,
        'wednesday_open': str(b.wednesday_open) if b.wednesday_open else None,
        'wednesday_close': str(b.wednesday_close) if b.wednesday_close else None,
        'thursday_open': str(b.thursday_open) if b.thursday_open else None,
        'thursday_close': str(b.thursday_close) if b.thursday_close else None,
        'friday_open': str(b.friday_open) if b.friday_open else None,
        'friday_close': str(b.friday_close) if b.friday_close else None,
        'saturday_open': str(b.saturday_open) if b.saturday_open else None,
        'saturday_close': str(b.saturday_close) if b.saturday_close else None,
        'sunday_open': str(b.sunday_open) if b.sunday_open else None,
        'sunday_close': str(b.sunday_close) if b.sunday_close else None,
        'is_active': b.is_active,
        'created_at': b.created_at.isoformat() if b.created_at else None,
    }


class BranchListCreateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def get(self, request):
        user = request.user
        queryset = Branch.objects.select_related('institute', 'city', 'state').all()
        institute_id = request.query_params.get('institute')
        city = request.query_params.get('city')
        state = request.query_params.get('state')
        is_active = request.query_params.get('is_active')
        search = request.query_params.get('search')
        if institute_id:
            queryset = queryset.filter(institute_id=institute_id)
        if city:
            queryset = queryset.filter(city_id=city)
        if state:
            queryset = queryset.filter(state_id=state)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('true', '1'))
        if search:
            queryset = queryset.filter(name__icontains=search)
        if user.is_authenticated and user.role == 'institute_owner':
            queryset = queryset.filter(institute__owner=user)
        elif not user.is_authenticated or user.role not in ('admin',):
            queryset = queryset.filter(is_active=True)
        queryset = queryset.order_by('-created_at')
        return Response([branch_to_dict(b) for b in queryset])

    def post(self, request):
        user = request.user
        institute_id = request.data.get('institute')
        name = request.data.get('name', '').strip()
        address = request.data.get('address', '').strip()
        contact_number = request.data.get('contact_number', '').strip()
        if not institute_id:
            return Response({'error': 'Institute is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not address:
            return Response({'error': 'Address is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not contact_number:
            return Response({'error': 'Contact number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            institute = Institute.objects.get(id=institute_id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role != 'admin' and institute.owner != user:
            return Response({'error': 'You do not own this institute.'}, status=status.HTTP_403_FORBIDDEN)
        city_id = request.data.get('city')
        state_id = request.data.get('state')
        city_obj = None
        state_obj = None
        if city_id:
            from common.models import City as CityModel
            try:
                city_obj = CityModel.objects.get(id=city_id)
            except CityModel.DoesNotExist:
                return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        if state_id:
            from common.models import State as StateModel
            try:
                state_obj = StateModel.objects.get(id=state_id)
            except StateModel.DoesNotExist:
                return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        branch = Branch.objects.create(
            institute=institute,
            name=name,
            address=address,
            city=city_obj,
            state=state_obj,
            pincode=request.data.get('pincode', ''),
            contact_number=contact_number,
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude'),
            monday_open=request.data.get('monday_open'),
            monday_close=request.data.get('monday_close'),
            tuesday_open=request.data.get('tuesday_open'),
            tuesday_close=request.data.get('tuesday_close'),
            wednesday_open=request.data.get('wednesday_open'),
            wednesday_close=request.data.get('wednesday_close'),
            thursday_open=request.data.get('thursday_open'),
            thursday_close=request.data.get('thursday_close'),
            friday_open=request.data.get('friday_open'),
            friday_close=request.data.get('friday_close'),
            saturday_open=request.data.get('saturday_open'),
            saturday_close=request.data.get('saturday_close'),
            sunday_open=request.data.get('sunday_open'),
            sunday_close=request.data.get('sunday_close'),
            is_active=request.data.get('is_active', True),
        )
        branch = Branch.objects.select_related('institute', 'city', 'state').get(id=branch.id)
        return Response(branch_to_dict(branch), status=status.HTTP_201_CREATED)


class BranchDetailView(APIView):
    permission_classes = []

    def get(self, request, id):
        try:
            branch = Branch.objects.select_related('institute', 'city', 'state').get(id=id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(branch_to_dict(branch))


class BranchUpdateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def put(self, request, id):
        user = request.user
        try:
            branch = Branch.objects.select_related('institute', 'city', 'state').get(id=id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role != 'admin' and branch.institute.owner != user:
            return Response({'error': 'You do not own this institute.'}, status=status.HTTP_403_FORBIDDEN)
        name = request.data.get('name', '').strip()
        address = request.data.get('address', '').strip()
        contact_number = request.data.get('contact_number', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not address:
            return Response({'error': 'Address is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not contact_number:
            return Response({'error': 'Contact number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        city_id = request.data.get('city')
        state_id = request.data.get('state')
        if city_id:
            from common.models import City as CityModel
            try:
                branch.city = CityModel.objects.get(id=city_id)
            except CityModel.DoesNotExist:
                return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        if state_id:
            from common.models import State as StateModel
            try:
                branch.state = StateModel.objects.get(id=state_id)
            except StateModel.DoesNotExist:
                return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        branch.name = name
        branch.address = address
        branch.contact_number = contact_number
        branch.pincode = request.data.get('pincode', branch.pincode)
        branch.is_active = bool(request.data.get('is_active', branch.is_active))
        time_fields = [
            'latitude', 'longitude',
            'monday_open', 'monday_close',
            'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close',
            'thursday_open', 'thursday_close',
            'friday_open', 'friday_close',
            'saturday_open', 'saturday_close',
            'sunday_open', 'sunday_close',
        ]
        for field in time_fields:
            if field in request.data:
                setattr(branch, field, request.data.get(field))
        branch.save()
        branch = Branch.objects.select_related('institute', 'city', 'state').get(id=branch.id)
        return Response(branch_to_dict(branch))

    def patch(self, request, id):
        user = request.user
        try:
            branch = Branch.objects.select_related('institute', 'city', 'state').get(id=id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        if user.role != 'admin' and branch.institute.owner != user:
            return Response({'error': 'You do not own this institute.'}, status=status.HTTP_403_FORBIDDEN)
        if 'name' in request.data:
            branch.name = request.data['name']
        if 'address' in request.data:
            branch.address = request.data['address']
        if 'contact_number' in request.data:
            branch.contact_number = request.data['contact_number']
        if 'pincode' in request.data:
            branch.pincode = request.data['pincode']
        if 'is_active' in request.data:
            branch.is_active = bool(request.data['is_active'])
        if 'city' in request.data and request.data['city']:
            from common.models import City as CityModel
            try:
                branch.city = CityModel.objects.get(id=request.data['city'])
            except CityModel.DoesNotExist:
                return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        if 'state' in request.data and request.data['state']:
            from common.models import State as StateModel
            try:
                branch.state = StateModel.objects.get(id=request.data['state'])
            except StateModel.DoesNotExist:
                return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        time_fields = [
            'latitude', 'longitude',
            'monday_open', 'monday_close',
            'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close',
            'thursday_open', 'thursday_close',
            'friday_open', 'friday_close',
            'saturday_open', 'saturday_close',
            'sunday_open', 'sunday_close',
        ]
        for field in time_fields:
            if field in request.data:
                setattr(branch, field, request.data.get(field))
        branch.save()
        branch = Branch.objects.select_related('institute', 'city', 'state').get(id=branch.id)
        return Response(branch_to_dict(branch))


class BranchDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            branch = Branch.objects.get(id=id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstituteBranchesView(APIView):
    permission_classes = []

    def get(self, request, institute_id):
        try:
            Institute.objects.get(id=institute_id)
        except Institute.DoesNotExist:
            return Response({'error': 'Institute not found.'}, status=status.HTTP_404_NOT_FOUND)
        queryset = Branch.objects.select_related('institute', 'city', 'state').filter(
            institute_id=institute_id, is_active=True
        ).order_by('-created_at')
        return Response([branch_to_dict(b) for b in queryset])
