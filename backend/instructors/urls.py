from django.urls import path
from . import views

app_name = 'instructors'

urlpatterns = [
    path('instructors/', views.InstructorListView.as_view(), name='instructor-list'),
    path('instructors/create/', views.InstructorCreateView.as_view(), name='instructor-create'),
    path('instructors/<int:id>/', views.InstructorDetailView.as_view(), name='instructor-detail'),
    path('instructors/<int:id>/update/', views.InstructorUpdateView.as_view(), name='instructor-update'),
    path('instructors/<int:id>/delete/', views.InstructorDeleteView.as_view(), name='instructor-delete'),
    path('branches/<int:branch_id>/instructors/', views.BranchInstructorsView.as_view(), name='branch-instructors'),
    path('branches/<int:branch_id>/available-instructors/', views.AvailableInstructorsView.as_view(), name='available-instructors'),
]
