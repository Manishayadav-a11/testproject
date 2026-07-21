from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Vehicle
from branches.models import Branch
from common.permissions import IsAdmin, IsInstituteOwnerOrAdmin


def vehicle_to_dict(v):
    return {
        'id': v.id,
        'branch': v.branch_id,
        'branch_name': v.branch.name,
        'registration_number': v.registration_number,
        'vehicle_type': v.vehicle_type,
        'transmission': v.transmission,
        'brand': v.brand,
        'model_name': v.model_name,
        'color': v.color,
        'year_of_manufacture': v.year_of_manufacture,
        'insurance_valid_upto': str(v.insurance_valid_upto) if v.insurance_valid_upto else None,
        'fitness_certificate_valid_upto': str(v.fitness_certificate_valid_upto) if v.fitness_certificate_valid_upto else None,
        'is_available': v.is_available,
        'created_at': v.created_at.isoformat() if v.created_at else None,
    }


class VehicleListCreateView(APIView):
    def get(self, request):
        qs = Vehicle.objects.select_related('branch').all()
        branch = request.query_params.get('branch')
        if branch:
            qs = qs.filter(branch_id=branch)
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        transmission = request.query_params.get('transmission')
        if transmission:
            qs = qs.filter(transmission=transmission)
        data = [vehicle_to_dict(v) for v in qs]
        return Response(data)

    permission_classes = [IsInstituteOwnerOrAdmin]

    def post(self, request):
        data = request.data
        branch_id = data.get('branch_id')
        registration_number = data.get('registration_number')
        if not branch_id:
            return Response({'error': 'branch_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not registration_number:
            return Response({'error': 'registration_number is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            branch = Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.role != 'admin':
            if not hasattr(branch.institute, 'owner') or branch.institute.owner != request.user:
                return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        if Vehicle.objects.filter(registration_number=registration_number).exists():
            return Response({'error': 'A vehicle with this registration number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        vehicle_type_val = data.get('vehicle_type', 'car')
        transmission_val = data.get('transmission', 'manual')
        if vehicle_type_val not in dict(Vehicle.VehicleType.choices):
            return Response({'error': f'vehicle_type must be one of: {", ".join(dict(Vehicle.VehicleType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        if transmission_val not in dict(Vehicle.TransmissionType.choices):
            return Response({'error': f'transmission must be one of: {", ".join(dict(Vehicle.TransmissionType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        vehicle = Vehicle.objects.create(
            branch=branch,
            registration_number=registration_number,
            vehicle_type=vehicle_type_val,
            transmission=transmission_val,
            brand=data.get('brand', ''),
            model_name=data.get('model_name', ''),
            color=data.get('color', ''),
            year_of_manufacture=data.get('year_of_manufacture'),
            insurance_valid_upto=data.get('insurance_valid_upto'),
            fitness_certificate_valid_upto=data.get('fitness_certificate_valid_upto'),
            is_available=data.get('is_available', True),
        )
        return Response(vehicle_to_dict(vehicle), status=status.HTTP_201_CREATED)


class VehicleDetailView(APIView):
    def get(self, request, id):
        try:
            vehicle = Vehicle.objects.select_related('branch').get(pk=id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(vehicle_to_dict(vehicle))


class VehicleUpdateView(APIView):
    permission_classes = [IsInstituteOwnerOrAdmin]

    def _check_permission(self, request, vehicle):
        if request.user.role == 'admin':
            return True
        return hasattr(vehicle.branch.institute, 'owner') and vehicle.branch.institute.owner == request.user

    def _update(self, request, id):
        try:
            vehicle = Vehicle.objects.select_related('branch', 'branch__institute').get(pk=id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not self._check_permission(request, vehicle):
            return Response({'error': 'You do not own this branch.'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        if request.method == 'PUT':
            required_fields = ['registration_number', 'vehicle_type', 'transmission', 'brand', 'model_name', 'color']
            missing = [f for f in required_fields if f not in data]
            if missing:
                return Response({'error': f'The following fields are required: {", ".join(missing)}.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'registration_number' in data:
            reg = data['registration_number']
            if Vehicle.objects.filter(registration_number=reg).exclude(pk=id).exists():
                return Response({'error': 'A vehicle with this registration number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            vehicle.registration_number = reg
        if 'vehicle_type' in data:
            if data['vehicle_type'] not in dict(Vehicle.VehicleType.choices):
                return Response({'error': f'vehicle_type must be one of: {", ".join(dict(Vehicle.VehicleType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
            vehicle.vehicle_type = data['vehicle_type']
        if 'transmission' in data:
            if data['transmission'] not in dict(Vehicle.TransmissionType.choices):
                return Response({'error': f'transmission must be one of: {", ".join(dict(Vehicle.TransmissionType.choices).keys())}'}, status=status.HTTP_400_BAD_REQUEST)
            vehicle.transmission = data['transmission']
        if 'brand' in data:
            vehicle.brand = data['brand']
        if 'model_name' in data:
            vehicle.model_name = data['model_name']
        if 'color' in data:
            vehicle.color = data['color']
        if 'year_of_manufacture' in data:
            vehicle.year_of_manufacture = data['year_of_manufacture']
        if 'insurance_valid_upto' in data:
            vehicle.insurance_valid_upto = data['insurance_valid_upto']
        if 'fitness_certificate_valid_upto' in data:
            vehicle.fitness_certificate_valid_upto = data['fitness_certificate_valid_upto']
        if 'is_available' in data:
            vehicle.is_available = bool(data['is_available'])
        vehicle.save()
        return Response(vehicle_to_dict(vehicle))

    def put(self, request, id):
        return self._update(request, id)

    def patch(self, request, id):
        return self._update(request, id)


class VehicleDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id):
        try:
            vehicle = Vehicle.objects.get(pk=id)
        except Vehicle.DoesNotExist:
            return Response({'error': 'Vehicle not found.'}, status=status.HTTP_404_NOT_FOUND)
        vehicle.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BranchVehiclesView(APIView):
    def get(self, request, branch_id):
        try:
            Branch.objects.get(id=branch_id)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found.'}, status=status.HTTP_404_NOT_FOUND)
        qs = Vehicle.objects.select_related('branch').filter(branch_id=branch_id)
        vehicle_type = request.query_params.get('vehicle_type')
        if vehicle_type:
            qs = qs.filter(vehicle_type=vehicle_type)
        transmission = request.query_params.get('transmission')
        if transmission:
            qs = qs.filter(transmission=transmission)
        data = [vehicle_to_dict(v) for v in qs]
        return Response(data)
