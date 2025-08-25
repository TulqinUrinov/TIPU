from django.contrib.messages import success
from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView

from SMS.sms import SayqalSms
from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType
from data.student.models import Student
from data.student.serializers import *


# O'quv yiliga tegishli barcha talabalar ro'yxati uchun
class StudentEduYearListApiView(generics.ListAPIView):
    serializer_class = StudentEduYearSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedUserType]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "full_name",
        "jshshir",
        "user_account__phone_number",
    ]

    def get_queryset(self):
        edu_year = self.kwargs.get('edu_year')
        return Student.objects.filter(student_years__education_year_id=edu_year)


# Retrieve
class StudentGetApiView(generics.RetrieveAPIView):
    queryset = Student.objects.filter(is_archived=False)
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticatedUserType]


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
        jshshir_list = serializer.validated_data["students"]

        sms_client = SayqalSms()
        success, failed = [], []

        for jshshir in jshshir_list:
            try:
                student = Student.objects.get(jshshir=jshshir)
            except Student.DoesNotExist:
                failed.append({"jshshir": jshshir, "error": "Student not found"})
                continue

            phone_number = getattr(student.user_account, "phone_number", None)

            if phone_number:
                response = sms_client.send_sms(phone_number, message)
                if response.status_code == status.HTTP_200_OK:
                    success.append({"jshshir": jshshir, "student": student.full_name})
                else:
                    failed.append({
                        "jshshir": jshshir,
                        "student": student.full_name,
                        "error": response.text
                    })

            else:
                failed.append({
                    "jshshir": jshshir,
                    "student": student.full_name,
                    "error": "Phone number not found."
                })

        return Response({
            "success": success,
            "failed": failed},
            status=status.HTTP_200_OK

        )
