from rest_framework import generics

from data.common.permission import IsAuthenticatedUserType
from data.faculty.models import Faculty
from data.faculty.serializers import FacultySeriazlizer


class FacultyListAPIView(generics.ListAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySeriazlizer
    permission_classes = [IsAuthenticatedUserType]
