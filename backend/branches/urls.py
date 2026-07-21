from django.urls import path
from . import views

app_name = 'branches'

urlpatterns = [
    path('branches/', views.BranchListCreateView.as_view(), name='branch-list'),
    path('branches/<int:id>/', views.BranchDetailView.as_view(), name='branch-detail'),
    path('branches/<int:id>/update/', views.BranchUpdateView.as_view(), name='branch-update'),
    path('branches/<int:id>/delete/', views.BranchDeleteView.as_view(), name='branch-delete'),
    path('institutes/<int:institute_id>/branches/', views.InstituteBranchesView.as_view(), name='institute-branches'),
]
