from decimal import Decimal

from rest_framework import viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from data.common.permission import IsAuthenticatedUserType

from rest_framework import viewsets, mixins
from .models import InstallmentPayment, Payment
from .serializers import InstallmentPaymentSerializer, PaymentHistorySerializer, InstallmentBulkUpdateSerializer
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


class InstallmentPaymentBulkUpdateAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def put(self, request):
        serializer = InstallmentBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        installment_count = validated['installment_count']
        payment_dates = validated['payment_dates']

        qs = InstallmentPayment.objects.filter(custom=False)
        updated = []

        for obj in qs:
            total_left = obj.left
            if installment_count == 0:
                continue

            # teng taqsimlash
            amount_per_split = (total_left / Decimal(installment_count)).quantize(Decimal("0.01"))

            splits = []
            for date in payment_dates:
                splits.append({
                    "left": float(amount_per_split),
                    "amount": str(amount_per_split),
                    "payment_date": date.isoformat() if hasattr(date, "isoformat") else str(date)
                })

            # obyektni update qilish
            obj.installment_count = installment_count
            obj.installment_payments = splits
            obj.save()

            updated.append(InstallmentPaymentSerializer(obj).data)

        return Response(updated, status=status.HTTP_200_OK)


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
