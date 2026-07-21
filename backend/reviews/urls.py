from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:id>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('reviews/<int:id>/update/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('reviews/<int:id>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('my-reviews/', views.MyReviewsView.as_view(), name='my-reviews'),
    path('institute-reviews/<int:institute_id>/', views.InstituteReviewsView.as_view(), name='institute-reviews'),
    path('instructor-reviews/<int:instructor_id>/', views.InstructorReviewsView.as_view(), name='instructor-reviews'),
    path('course-reviews/<int:course_id>/', views.CourseReviewsView.as_view(), name='course-reviews'),
]
