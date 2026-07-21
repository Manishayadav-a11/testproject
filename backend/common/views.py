from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import State, City, Category
from .permissions import IsAdmin, IsAdminOrReadOnly


def state_to_dict(s):
    return {'id': s.id, 'name': s.name, 'is_active': s.is_active}


def city_to_dict(c):
    return {'id': c.id, 'name': c.name, 'state': c.state_id, 'state_name': c.state.name if c.state else None, 'is_active': c.is_active}


def category_to_dict(cat):
    return {'id': cat.id, 'name': cat.name, 'description': cat.description, 'icon': cat.icon, 'is_active': cat.is_active}


class StateListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = State.objects.all().order_by('-created_at')
        name = request.query_params.get('name')
        is_active = request.query_params.get('is_active')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('true', '1'))
        return Response([state_to_dict(s) for s in queryset])

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if State.objects.filter(name__iexact=name).exists():
            return Response({'error': 'State with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        is_active = request.data.get('is_active', True)
        state = State.objects.create(name=name, is_active=bool(is_active))
        return Response(state_to_dict(state), status=status.HTTP_201_CREATED)


class StateDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, id):
        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(state_to_dict(state))

    def put(self, request, id):
        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        is_active = request.data.get('is_active', True)
        if name != state.name and State.objects.filter(name__iexact=name).exists():
            return Response({'error': 'State with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        state.name = name
        state.is_active = bool(is_active)
        state.save()
        return Response(state_to_dict(state))

    def patch(self, request, id):
        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', state.name)
        is_active = request.data.get('is_active', state.is_active)
        if name != state.name and State.objects.filter(name__iexact=name).exists():
            return Response({'error': 'State with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        state.name = name
        state.is_active = bool(is_active)
        state.save()
        return Response(state_to_dict(state))

    def delete(self, request, id):
        try:
            state = State.objects.get(pk=id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CityListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = City.objects.select_related('state').all().order_by('-created_at')
        name = request.query_params.get('name')
        state = request.query_params.get('state')
        is_active = request.query_params.get('is_active')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if state:
            queryset = queryset.filter(state_id=state)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('true', '1'))
        return Response([city_to_dict(c) for c in queryset])

    def post(self, request):
        name = request.data.get('name', '').strip()
        state_id = request.data.get('state')
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not state_id:
            return Response({'error': 'State is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            state_obj = State.objects.get(id=state_id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        if City.objects.filter(state=state_obj, name__iexact=name).exists():
            return Response({'error': 'City with this name already exists in this state.'}, status=status.HTTP_400_BAD_REQUEST)
        is_active = request.data.get('is_active', True)
        city = City.objects.create(state=state_obj, name=name, is_active=bool(is_active))
        city = City.objects.select_related('state').get(id=city.id)
        return Response(city_to_dict(city), status=status.HTTP_201_CREATED)


class CityDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, id):
        try:
            city = City.objects.select_related('state').get(pk=id)
        except City.DoesNotExist:
            return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(city_to_dict(city))

    def put(self, request, id):
        try:
            city = City.objects.select_related('state').get(pk=id)
        except City.DoesNotExist:
            return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', '').strip()
        state_id = request.data.get('state')
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not state_id:
            return Response({'error': 'State is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            state_obj = State.objects.get(id=state_id)
        except State.DoesNotExist:
            return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
        if (name != city.name or state_id != city.state_id):
            if City.objects.filter(state_id=state_id, name__iexact=name).exclude(pk=id).exists():
                return Response({'error': 'City with this name already exists in this state.'}, status=status.HTTP_400_BAD_REQUEST)
        city.name = name
        city.state = state_obj
        if 'is_active' in request.data:
            city.is_active = bool(request.data['is_active'])
        city.save()
        city = City.objects.select_related('state').get(id=city.id)
        return Response(city_to_dict(city))

    def patch(self, request, id):
        try:
            city = City.objects.select_related('state').get(pk=id)
        except City.DoesNotExist:
            return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', city.name)
        state_id = request.data.get('state', city.state_id)
        is_active = request.data.get('is_active', city.is_active)
        if (name != city.name or state_id != city.state_id):
            if City.objects.filter(state_id=state_id, name__iexact=name).exclude(pk=id).exists():
                return Response({'error': 'City with this name already exists in this state.'}, status=status.HTTP_400_BAD_REQUEST)
        if state_id != city.state_id:
            try:
                state_obj = State.objects.get(id=state_id)
            except State.DoesNotExist:
                return Response({'error': 'State not found.'}, status=status.HTTP_404_NOT_FOUND)
            city.state = state_obj
        city.name = name
        city.is_active = bool(is_active)
        city.save()
        city = City.objects.select_related('state').get(id=city.id)
        return Response(city_to_dict(city))

    def delete(self, request, id):
        try:
            city = City.objects.get(pk=id)
        except City.DoesNotExist:
            return Response({'error': 'City not found.'}, status=status.HTTP_404_NOT_FOUND)
        city.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        queryset = Category.objects.all().order_by('-created_at')
        name = request.query_params.get('name')
        is_active = request.query_params.get('is_active')
        if name:
            queryset = queryset.filter(name__icontains=name)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in ('true', '1'))
        return Response([category_to_dict(c) for c in queryset])

    def post(self, request):
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if Category.objects.filter(name__iexact=name).exists():
            return Response({'error': 'Category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get('description', '')
        icon = request.data.get('icon', '')
        is_active = request.data.get('is_active', True)
        category = Category.objects.create(name=name, description=description, icon=icon, is_active=bool(is_active))
        return Response(category_to_dict(category), status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, id):
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(category_to_dict(category))

    def put(self, request, id):
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', '').strip()
        if not name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        description = request.data.get('description', '')
        icon = request.data.get('icon', '')
        is_active = request.data.get('is_active', True)
        if name != category.name and Category.objects.filter(name__iexact=name).exists():
            return Response({'error': 'Category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        category.name = name
        category.description = description
        category.icon = icon
        category.is_active = bool(is_active)
        category.save()
        return Response(category_to_dict(category))

    def patch(self, request, id):
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        name = request.data.get('name', category.name)
        description = request.data.get('description', category.description)
        icon = request.data.get('icon', category.icon)
        is_active = request.data.get('is_active', category.is_active)
        if name != category.name and Category.objects.filter(name__iexact=name).exists():
            return Response({'error': 'Category with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        category.name = name
        category.description = description
        category.icon = icon
        category.is_active = bool(is_active)
        category.save()
        return Response(category_to_dict(category))

    def delete(self, request, id):
        try:
            category = Category.objects.get(pk=id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
