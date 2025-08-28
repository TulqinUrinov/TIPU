import openpyxl
from django.db.models.functions import Coalesce, NullIf
from openpyxl.styles import Alignment, Font, Border, Side
from rest_framework import generics, filters, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.http import HttpResponse

from data.contract.models import Contract
from sms.sayqal import SayqalSms
from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType

from data.student.serializers import *

# O'quv yiliga tegishli barcha talabalar ro'yxati uchun
from django.db.models import Q, Value, F, OuterRef, Subquery, DecimalField, ExpressionWrapper, Count, Avg


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
        percentage_range = self.request.query_params.get('percentage')
        type_filter = self.request.query_params.get('type')

        # queryset = Student.objects.filter(
        #     student_years__education_year_id=edu_year
        # )

        queryset = Student.objects.filter(
            student_years__education_year_id=edu_year
        ).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            left=Coalesce(
                Sum("contract_payments__left"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
        ).annotate(
            total_paid=F("contract_amount") - F("left"),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100, output_field=DecimalField()))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField())),
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

        # HEMIS / NO-HEMIS bo‘yicha filter
        if type_filter == "hemis":
            queryset = queryset.filter(user_account__isnull=True)
        if type_filter == "no-hemis":
            queryset = queryset.filter(user_account__isnull=False)

        # percentage bo‘yicha filter
        if percentage_range:
            if "-" in percentage_range:
                start, end = map(float, percentage_range.split("-"))
                queryset = queryset.filter(
                    percentage__gte=start,
                    percentage__lte=end
                )
            else:
                value = float(percentage_range)
                queryset = queryset.filter(percentage=value)

        return queryset.distinct()


class StudentEduYearExcelExportApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self):
        edu_year = self.kwargs.get('edu_year')
        course = self.request.query_params.get('course')
        faculty_ids = self.request.query_params.get('faculty')
        percentage_range = self.request.query_params.get('percentage')
        type_filter = self.request.query_params.get('type')
        print(type_filter)

        queryset = Student.objects.filter(
            student_years__education_year_id=edu_year
        ).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            left=Coalesce(
                Sum("contract_payments__left"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
        ).annotate(
            total_paid=F("contract_amount") - F("left"),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100, output_field=DecimalField()))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField())),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )

        if course:
            queryset = queryset.filter(course=course)

        if faculty_ids:
            faculty_list = [int(f_id) for f_id in faculty_ids.split(",")]
            queryset = queryset.filter(specialization__faculty_id__in=faculty_list)

        if type_filter == "hemis":
            queryset = queryset.filter(user_account__isnull=True)
        if type_filter == "no-hemis":
            print(type_filter)
            queryset = queryset.filter(user_account__isnull=False)

        if percentage_range:
            start, end = map(float, percentage_range.split("-"))
            queryset = queryset.filter(
                percentage__gte=start,
                percentage__lte=end
            )

        return queryset.distinct()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Excel fayl yaratamiz
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Talabalar"

        # Header qator
        headers = [
            "F.I.Sh", "JSHSHIR", "Telefon",
            "Fakultet", "Mutaxassislik", "Guruh",
            "Kontrakt summasi", "To‘langan", "Qoldiq", "Foiz (%)"
        ]
        ws.append(headers)

        # Ma'lumotlarni yozish
        for student in queryset:
            print(student)
            ws.append([
                student.full_name,
                student.jshshir,
                student.user_account.phone_number if hasattr(student,
                                                             "user_account") and student.user_account else student.phone_number,
                student.specialization.faculty.name if student.specialization and student.specialization.faculty else "",
                student.specialization.name if student.specialization else "",
                student.group,
                float(student.contract_amount or 0),
                float(student.total_paid or 0),
                float(student.left or 0),
                float(student.percentage or 0),
            ])

        # Javobga yozib yuboramiz
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="students.xlsx"'
        wb.save(response)
        return response


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

    def get(self, request, edu_year):
        course = request.query_params.get("course")  # masalan: ?course=1-kurs
        faculty_ids = request.query_params.get("faculty")  # masalan: ?faculty=1,2,3

        filters = {"is_archived": False}
        if course:
            filters["course"] = course
        if faculty_ids:
            faculty_list = [int(f_id) for f_id in faculty_ids.split(",") if f_id.isdigit()]
            filters["specialization__faculty_id__in"] = faculty_list

        serializer = StudentStatisticsSerializer(
            instance=Student(),
            context={
                "filters": filters,
                "request": request,
                "edu_year": edu_year,
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentStatisticsExcelApiView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def get_queryset(self, request):
        course = request.query_params.get("course")
        faculty_ids = request.query_params.get("faculty")
        percentage_range = request.query_params.get("percentage")

        filters = {"is_archived": False}
        if course:
            filters["course"] = course
        if faculty_ids:
            faculty_list = [int(f_id) for f_id in faculty_ids.split(",") if f_id.isdigit()]
            filters["specialization__faculty_id__in"] = faculty_list

        qs = Student.objects.filter(**filters).annotate(
            contract_amount=Coalesce(
                F("contract__period_amount_dt"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            left_sum=Coalesce(
                Sum("contract_payments__left"),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
        ).annotate(
            total_paid=F("contract_amount") - F("left_sum"),
            percentage=ExpressionWrapper(
                (F("total_paid") * Value(100, output_field=DecimalField()))
                / NullIf(F("contract_amount"), Value(0, output_field=DecimalField())),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        )

        # Foiz filteri

        if percentage_range:
            if "-" in percentage_range:
                start, end = map(float, percentage_range.split("-"))
                qs = qs.filter(percentage__gte=start, percentage__lte=end)
            else:
                value = float(percentage_range)
                qs = qs.filter(percentage=value)

        return qs

    def get_faculty_stats(self, queryset):
        stats = []
        faculties = queryset.values("specialization__faculty__name").annotate(
            total_students=Count("id")
        )

        for fac in faculties:
            faculty_name = fac["specialization__faculty__name"] or "Noma’lum"
            total = fac["total_students"]

            paid = queryset.filter(
                specialization__faculty__name=faculty_name,
                percentage__gte=100
            ).count()

            not_paid = total - paid
            avg_percentage = queryset.filter(
                specialization__faculty__name=faculty_name
            ).aggregate(
                avg=Coalesce(
                    Avg("percentage"),
                    Value(0, output_field=DecimalField(max_digits=5, decimal_places=2))
                )
            )["avg"]

            # avg_percentage = queryset.filter(
            #     specialization__faculty__name=faculty_name
            # ).aggregate(avg=Coalesce(Avg("percentage"), Value(0)))["avg"]

            stats.append({
                "faculty": faculty_name,
                "total_students": total,
                "paid_students": paid,
                "not_paid_students": not_paid,
                "paid_percent": round((paid / total) * 100) if total else 0,
                "avg_percent": round(avg_percentage, 2),
            })
        return stats

    def get(self, request):
        queryset = self.get_queryset(request)
        results = self.get_faculty_stats(queryset)

        # Excel yaratish
        wb = Workbook()
        ws = wb.active
        ws.title = "Talabalar statistikasi"

        headers = [
            "№",
            "Dekanatlar",
            "Jami talabalar",
            "To‘liq to‘laganlar soni",
            "Qarzdorlar soni",
            "Foizda (to‘lagan)",
            "O‘rtacha foiz"
        ]
        ws.append(headers)

        jami_total = jami_paid = jami_not_paid = 0
        for i, row in enumerate(results, start=1):
            ws.append([
                i,
                row["faculty"],
                row["total_students"],
                row["paid_students"],
                row["not_paid_students"],
                f"{row['paid_percent']}%",
                row["avg_percent"]
            ])

            jami_total += row["total_students"]
            jami_paid += row["paid_students"]
            jami_not_paid += row["not_paid_students"]

        # Oxirgi qator Jami
        jami_percent = round((jami_paid / jami_total) * 100) if jami_total else 0
        avg_percent = round(
            queryset.aggregate(
                avg=Coalesce(
                    Avg("percentage"),
                    Value(0, output_field=DecimalField(max_digits=5, decimal_places=2))
                )
            )["avg"],
            2
        )

        # avg_percent = round(
        #     queryset.aggregate(avg=Coalesce(Avg("percentage"), Value(0)))["avg"], 2
        # )
        ws.append([
            "Jami",
            "",
            jami_total,
            jami_paid,
            jami_not_paid,
            f"{jami_percent}%",
            avg_percent
        ])

        # Javob sifatida yuborish
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="student_statistics.xlsx"'
        wb.save(response)
        return response


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

        # Agar frontend "send_all": true yuborsa → barcha studentlarni olish
        if send_all:
            students = Student.objects.all()
        else:
            students = Student.objects.filter(jshshir__in=jshshir_list)

        for student in students:

            student_user = getattr(student, "user_account", None)
            phone_number = None

            if student_user and student_user.phone_number:
                phone_number = student_user.phone_number
            elif student.phone_number:
                phone_number = student.phone_number

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
