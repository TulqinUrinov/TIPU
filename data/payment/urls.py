from rest_framework import routers
from django.urls import path, include
from data.payment.views import (
    InstallmentPaymentViewSet,
    PaymentHistoryApiView,
    InstallmentPaymentBulkUpdateAPIView,
    InstallmentPaymentConfigAPIView,
    ReminderConfigViewSet
)

router = routers.DefaultRouter()
router.register(r"installments", InstallmentPaymentViewSet)
router.register("reminder-configs", ReminderConfigViewSet, basename="reminder-configs")

urlpatterns = [
    path("bulk-update/", InstallmentPaymentBulkUpdateAPIView.as_view(),
         name="installment-bulk-update"),
    path('history/', PaymentHistoryApiView.as_view(), name='payment-history'),
    path('settings/', InstallmentPaymentConfigAPIView.as_view()),


] + router.urls
