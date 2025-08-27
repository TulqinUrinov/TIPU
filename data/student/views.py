from django.db.models.functions import Coalesce, NullIf
from rest_framework import generics, filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

from data.contract.models import Contract
from sms.sayqal import SayqalSms
from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType

from data.student.serializers import *

# O'quv yiliga tegishli barcha talabalar ro'yxati uchun
from django.db.models import Q, Value, F, OuterRef, Subquery, DecimalField, ExpressionWrapper


class StudentEduYearListApiView(generics.ListAPIView):
    serializer_class = StudentEduYearSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedUserType]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "full_name",
        "jshshir",
        "user_account__phone_number",
        "phone_number"
    ]

    ordering_fields = ["full_name", "left"]  # faqat shu maydonlar bo‘yicha sortlashga ruxsat

    def get_queryset(self):
        edu_year = self.kwargs.get('edu_year')
        course = self.request.query_params.get('course')
        faculty_ids = self.request.query_params.get('faculty')
        percentage_ranges = self.request.query_params.get('percentage')

        # queryset = Student.objects.filter(
        #     student_years__education_year_id=edu_year
        # )

        queryset = Student.objects.filter(
            student_years__education_year_id=edu_year
        ).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
            ),
            total_paid=Coalesce(
                Sum("payments__amount", output_field=DecimalField(max_digits=12, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
            )
        ).annotate(
            left=ExpressionWrapper(
                F("contract_amount") - F("total_paid"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            ),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100.0, output_field=DecimalField(max_digits=5, decimal_places=2)))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )
        # Kurs bo‘yicha filter
        if course:
            queryset = queryset.filter(course=course)

        # Fakultet bo‘yicha filter
        if faculty_ids:
            faculty_list = [int(f_id) for f_id in faculty_ids.split(",")]
            queryset = queryset.filter(specialization__faculty_id__in=faculty_list)

        # Foiz bo‘yicha filter
        if percentage_ranges:
            start, end = percentage_ranges.split("-")
            queryset = queryset.filter(
                contract__payment_percentage__gte=float(start),
                contract__payment_percentage__lte=float(end)
            )

        return queryset.distinct()


# Retrieve
class StudentGetApiView(generics.RetrieveAPIView):
    queryset = Student.objects.filter(is_archived=False)
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedUserType]

    def get_object(self):
        # Admin bo‘lsa – hamma studentni ko‘rishi mumkin
        if getattr(self.request, "admin_user", None):
            return super().get_object()

        # Student bo‘lsa – faqat o‘zini ko‘ra olishi kerak
        if getattr(self.request, "student_user", None):
            student = Student.objects.filter(
                user_account=self.request.student_user,
                is_archived=False
            ).first()
            if not student:
                raise PermissionDenied("Siz faqat o‘zingizni ko‘rishingiz mumkin")
            return student

        raise PermissionDenied("Ruxsat yo‘q")


# Statistics
class StudentStatisticsApiView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def get(self, request):
        serializer = StudentStatisticsSerializer(instance=Student())
        return Response(serializer.data, status=status.HTTP_200_OK)


# Send Sms to choosen students
class SendSmsView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def post(self, request):
        serializer = SendSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.validated_data['message']
        jshshir_list = serializer.validated_data.get("students", [])
        send_all = serializer.validated_data.get("send_all", False)  # ✅ qo‘shimcha flag

        sms_client = SayqalSms()
        success, failed = [], []

        # ✅ Agar frontend "send_all": true yuborsa → barcha studentlarni olish
        if send_all:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(jshshir__in=jshshir_list)

        for student in students:

            student_user = getattr(student, "user_account", None)
            if student_user is None:
                # Student uchun user_account yo‘q – buni skip qilish yoki log qilish
                continue

            phone_number = student_user.phone_number
            # phone_number = getattr(student.user_account, "phone_number", None)

            if phone_number:
                response = sms_client.send_sms(phone_number, message)
                if response.status_code == status.HTTP_200_OK:
                    success.append({"jshshir": student.jshshir, "student": student.full_name})
                else:
                    failed.append({
                        "jshshir": student.jshshir,
                        "student": student.full_name,
                        "error": response.text
                    })
            else:
                failed.append({
                    "jshshir": student.jshshir,
                    "student": student.full_name,
                    "error": "Phone number not found."
                })

        return Response({
            "success": success,
            "failed": failed
        }, status=status.HTTP_200_OK)
