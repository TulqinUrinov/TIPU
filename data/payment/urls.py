from rest_framework import routers

from data.payment.views import InstallmentPaymentViewSet

router = routers.DefaultRouter()
router.register(r"", InstallmentPaymentViewSet)


urlpatterns = router.urls