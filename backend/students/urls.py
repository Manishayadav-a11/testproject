from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('students/', views.StudentListView.as_view(), name='student-list'),
    path('students/<int:id>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('students/profile/', views.StudentProfileView.as_view(), name='student-profile'),
]
