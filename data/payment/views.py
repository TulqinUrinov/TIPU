from rest_framework import viewsets, mixins, generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

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

    def update(self, request, *args, **kwargs):
        """Agar custom=True bo‘lsa skip qilinadi, qolganlarini update qilamiz"""
        instance = self.get_object()
        partial = kwargs.pop('partial', False)

        # agar bitta object update qilinayotgan bo‘lsa
        if instance.custom:
            return Response(
                {"detail": "Bu to‘lov custom bo‘lgani uchun update qilinmaydi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=False, methods=["put"], url_path="bulk-update")
    def bulk_update(self, request):
        """
        Barcha custom=False bo‘lgan InstallmentPayment larni update qilish
        """
        data = request.data
        qs = InstallmentPayment.objects.filter(custom=False)

        updated = []
        for obj in qs:
            serializer = self.get_serializer(obj, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            updated.append(serializer.data)

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
