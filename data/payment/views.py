from rest_framework import viewsets, mixins, generics
from rest_framework.exceptions import PermissionDenied

from data.common.permission import IsAuthenticatedUserType

from rest_framework import viewsets, mixins
from .models import InstallmentPayment, Payment
from .serializers import InstallmentPaymentSerializer, PaymentHistorySerializer
from ..student.models import Student


# Bo'lib to'lash
class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPayment.objects.all()
    serializer_class = InstallmentPaymentSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        # Agar student bo‘lsa faqat o‘zini ko‘rsin
        if getattr(self.request, "role", None) == "STUDENT" and self.request.student_user:
            student = self.request.student_user.student
            return InstallmentPayment.objects.filter(student=student)

        # ADMIN barchasini ko'rishi yoki student_id bo'yicha filter
        queryset = InstallmentPayment.objects.all()
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset


# To'lov tarixi
class PaymentHistoryApiView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):

        if getattr(self.request, "student_user", None):
            student = self.request.student_user.student
            return Payment.objects.filter(student=student).order_by("-payment_date")

        queryset = Payment.objects.all().order_by("-payment_date")
        student_jshshir = self.request.GET.get("student")
        if student_jshshir:
            return queryset.filter(student__jshshir=student_jshshir).order_by("-payment_date")
        return queryset
