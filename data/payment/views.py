from rest_framework import viewsets, mixins
from rest_framework.exceptions import PermissionDenied

from data.common.permission import IsAuthenticatedUserType

from rest_framework import viewsets, mixins
from .models import InstallmentPayment
from .serializers import InstallmentPaymentSerializer
from ..student.models import Student


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
            student = Student.objects.filter(user_account=self.request.student_user).first()
            if not student:
                raise PermissionDenied({"detail": "User not found", "code": "user_not_found"})
            return InstallmentPayment.objects.filter(student=student)

        # ADMIN barchasini ko'rishi yoki student_id bo'yicha filter
        queryset = InstallmentPayment.objects.all()
        student_id = self.request.GET.get("student")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        return queryset

    # def get_queryset(self):
    #     # STUDENT faqat o'zini ko'rsin
    #     if getattr(self.request, "role", None) == "STUDENT" and self.request.student_user:
    #         return InstallmentPayment.objects.filter(student=self.request.student_user)
    #
    #     # ADMIN barchasini ko'rishi yoki student_id bo'yicha filter
    #     queryset = InstallmentPayment.objects.all()
    #     student_id = self.request.GET.get("student")
    #     if student_id:
    #         queryset = queryset.filter(student_id=student_id)
    #     return queryset
