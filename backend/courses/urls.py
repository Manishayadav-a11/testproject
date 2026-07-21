from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('courses/', views.CourseListCreateView.as_view(), name='course-list'),
    path('courses/search/', views.CourseSearchView.as_view(), name='course-search'),
    path('courses/popular/', views.PopularCoursesView.as_view(), name='popular-courses'),
    path('courses/<int:id>/', views.CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:id>/update/', views.CourseUpdateView.as_view(), name='course-update'),
    path('courses/<int:id>/delete/', views.CourseDeleteView.as_view(), name='course-delete'),
    path('branches/<int:branch_id>/courses/', views.BranchCoursesView.as_view(), name='branch-courses'),
]
