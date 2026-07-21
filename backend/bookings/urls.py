from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('bookings/', views.BookingListView.as_view(), name='booking-list'),
    path('bookings/create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('bookings/<int:id>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('bookings/<int:id>/update/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('bookings/<int:id>/confirm/', views.BookingConfirmView.as_view(), name='booking-confirm'),
    path('bookings/<int:id>/cancel/', views.BookingCancelView.as_view(), name='booking-cancel'),
    path('my-bookings/', views.StudentBookingsView.as_view(), name='student-bookings'),
    path('institute-bookings/<int:institute_id>/', views.InstituteBookingsView.as_view(), name='institute-bookings'),
]
