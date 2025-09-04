from decimal import Decimal

from django.db import transaction
from rest_framework import generics, status

from rest_framework.response import Response
from rest_framework.views import APIView

from data.common.permission import IsAuthenticatedUserType

from rest_framework import viewsets, mixins
from .models import InstallmentPayment, Payment, ReminderConfig
from .serializers import InstallmentPaymentSerializer, PaymentHistorySerializer, InstallmentBulkUpdateSerializer, \
    ReminderConfigSerializer


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

        qs = InstallmentPayment.objects.filter(custom=False).select_related("student")

        updated_objs = []

        for obj in qs.iterator(chunk_size=1500):
            contract = obj.student.contract.first()
            if not contract:
                continue

            total_amount = contract.period_amount_dt
            amount_per_split = (total_amount / Decimal(installment_count)).quantize(Decimal("0.01"))

            splits = [
                {
                    "left": float(amount_per_split),
                    "amount": str(amount_per_split),
                    "payment_date": date.isoformat(),
                }
                for date in payment_dates
            ]

            obj.installment_count = installment_count
            obj.installment_payments = splits
            obj.left = float(amount_per_split * installment_count)

            updated_objs.append(obj)

        with transaction.atomic():
            InstallmentPayment.objects.bulk_update(
                updated_objs,
                ["installment_count", "installment_payments", "left"],
                batch_size=1000
            )

        return Response(
            {"updated": len(updated_objs),
             "installment_count": installment_count,
             "payment_dates": payment_dates},
            status=status.HTTP_200_OK
        )


class InstallmentPaymentConfigAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def get(self, request):
        obj = InstallmentPayment.objects.filter(custom=False).first()
        if not obj:
            return Response(
                {"detail": "Installment mavjud emas"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "installment_count": obj.installment_count,
                "payment_dates": [p["payment_date"] for p in obj.installment_payments],
            },
            status=status.HTTP_200_OK
        )


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


# Eslatma sms xabari
class ReminderConfigViewSet(viewsets.ModelViewSet):
    queryset = ReminderConfig.objects.all()
    serializer_class = ReminderConfigSerializer
    permission_classes = [IsAuthenticatedUserType]
