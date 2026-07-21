from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', views.PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<int:id>/process/', views.PaymentProcessView.as_view(), name='payment-process'),
    path('payments/<int:id>/refund/', views.PaymentRefundView.as_view(), name='payment-refund'),
    path('my-payments/', views.StudentPaymentsView.as_view(), name='student-payments'),
    path('institute-payments/<int:institute_id>/', views.InstitutePaymentsView.as_view(), name='institute-payments'),
]
