from rest_framework import viewsets

from data.common.permission import IsAuthenticatedUserType
from data.education_year.models import EducationYear
from data.education_year.serializers import EducationYearSerializer


class EducationYearViewSet(viewsets.ModelViewSet):
    queryset = EducationYear.objects.all()
    serializer_class = EducationYearSerializer
    permission_classes = [IsAuthenticatedUserType]
