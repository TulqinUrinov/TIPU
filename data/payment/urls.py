from rest_framework import routers
from django.urls import path
from data.payment.views import InstallmentPaymentViewSet, PaymentHistoryApiView

router = routers.DefaultRouter()
router.register(r"", InstallmentPaymentViewSet)

urlpatterns = [
                  path('history/', PaymentHistoryApiView.as_view(), name='payment-history'),
              ] + router.urls
