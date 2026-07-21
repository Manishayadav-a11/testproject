from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('vehicles/', views.VehicleListCreateView.as_view(), name='vehicle-list'),
    path('vehicles/<int:id>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('vehicles/<int:id>/update/', views.VehicleUpdateView.as_view(), name='vehicle-update'),
    path('vehicles/<int:id>/delete/', views.VehicleDeleteView.as_view(), name='vehicle-delete'),
    path('branches/<int:branch_id>/vehicles/', views.BranchVehiclesView.as_view(), name='branch-vehicles'),
]
