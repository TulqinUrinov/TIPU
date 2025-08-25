from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView

from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType
from data.student.models import Student
from data.student.serializers import StudentEduYearSerializer, StudentSerializer, StudentStatisticsSerializer


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
