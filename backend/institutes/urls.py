from django.urls import path
from . import views

app_name = 'institutes'

urlpatterns = [
    path('institutes/', views.InstituteListView.as_view(), name='institute-list'),
    path('institutes/create/', views.InstituteCreateView.as_view(), name='institute-create'),
    path('institutes/mine/', views.InstituteMineView.as_view(), name='institute-mine'),
    path('institutes/featured/', views.InstituteFeaturedView.as_view(), name='institute-featured'),
    path('institutes/search/', views.InstituteSearchView.as_view(), name='institute-search'),
    path('institutes/<int:id>/', views.InstituteDetailView.as_view(), name='institute-detail'),
    path('institutes/<int:id>/update/', views.InstituteUpdateView.as_view(), name='institute-update'),
    path('institutes/<int:id>/delete/', views.InstituteDeleteView.as_view(), name='institute-delete'),
    path('institutes/<int:id>/approve/', views.InstituteApproveView.as_view(), name='institute-approve'),
]
