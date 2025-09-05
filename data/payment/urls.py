from rest_framework import routers
from django.urls import path, include
from data.payment.views import (
    InstallmentPaymentViewSet,
    PaymentHistoryApiView,
    InstallmentPaymentBulkUpdateAPIView,
    InstallmentPaymentConfigAPIView,
    ReminderConfigViewSet,
    CancelPaymentAPIView,
    StudentActionHistoryAPIView,
)

router = routers.DefaultRouter()
router.register(r"installments", InstallmentPaymentViewSet)
router.register("reminder-configs", ReminderConfigViewSet, basename="reminder-configs")

urlpatterns = [
                  path("bulk-update/", InstallmentPaymentBulkUpdateAPIView.as_view(),
                       name="installment-bulk-update"),
                  # Student to'lovlari tarixi
                  path('history/', PaymentHistoryApiView.as_view(), name='payment-history'),
                  path('settings/', InstallmentPaymentConfigAPIView.as_view()),
                  # To'lovni bekor qilish
                  path("cancel/<int:pk>/", CancelPaymentAPIView.as_view(), name="cancel-payment"),
                  # Student action tarixlari
                  path("actions/", StudentActionHistoryAPIView.as_view(), name="student-actions"),

              ] + router.urls
