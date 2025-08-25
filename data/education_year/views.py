from rest_framework import viewsets, filters

from data.common.pagination import CustomPagination
from data.common.permission import IsAuthenticatedUserType
from data.education_year.models import EducationYear
from data.education_year.serializers import EducationYearSerializer


class EducationYearViewSet(viewsets.ModelViewSet):
    queryset = EducationYear.objects.all()
    serializer_class = EducationYearSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedUserType]
    filter_backends = [filters.SearchFilter]
    search_fields = ["edu_year"]
