from rest_framework import generics, filters

from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType
from data.student.models import Student
from data.student.serializers import StudentEduYearSerializer


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
