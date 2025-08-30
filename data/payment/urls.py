from rest_framework import routers
from django.urls import path
from data.payment.views import InstallmentPaymentViewSet, PaymentHistoryApiView, InstallmentPaymentBulkUpdateAPIView, \
    InstallmentPaymentConfigAPIView

router = routers.DefaultRouter()
router.register(r"", InstallmentPaymentViewSet)

urlpatterns = [
                  path("bulk-update/", InstallmentPaymentBulkUpdateAPIView.as_view(),
                       name="installment-bulk-update"),
                  path('history/', PaymentHistoryApiView.as_view(), name='payment-history'),
                  path('settings/', InstallmentPaymentConfigAPIView.as_view())
              ] + router.urls
