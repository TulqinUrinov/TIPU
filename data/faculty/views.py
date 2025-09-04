from rest_framework.viewsets import ModelViewSet
from .models import Faculty
from .serializers import FacultySerializer
from data.common.permission import IsAuthenticatedUserType


class FacultyViewSet(ModelViewSet):
    queryset = Faculty.objects.all().prefetch_related("specializations")
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticatedUserType]
