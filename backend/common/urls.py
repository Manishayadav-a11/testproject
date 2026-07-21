from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('states/', views.StateListCreateView.as_view(), name='state-list'),
    path('states/<int:id>/', views.StateDetailView.as_view(), name='state-detail'),
    path('cities/', views.CityListCreateView.as_view(), name='city-list'),
    path('cities/<int:id>/', views.CityDetailView.as_view(), name='city-detail'),
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:id>/', views.CategoryDetailView.as_view(), name='category-detail'),
]
