from rest_framework import viewsets, mixins

from data.common.permission import IsAuthenticatedUserType

from rest_framework import viewsets, mixins
from .models import InstallmentPayment
from .serializers import InstallmentPaymentSerializer


# class InstallmentPaymentViewSet(mixins.CreateModelMixin,
#                                 mixins.ListModelMixin,
#                                 mixins.UpdateModelMixin,
#                                 mixins.RetrieveModelMixin,
#                                 viewsets.GenericViewSet):

class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    queryset = InstallmentPayment.objects.all()
    serializer_class = InstallmentPaymentSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        # STUDENT faqat o'zini ko'rsin
        if getattr(self.request, "role", None) == "STUDENT" and self.request.student_user:
            return InstallmentPayment.objects.filter(student=self.request.student_user)

        # ADMIN barchasini ko'rishi yoki student_id bo'yicha filter
        queryset = InstallmentPayment.objects.all()
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset
