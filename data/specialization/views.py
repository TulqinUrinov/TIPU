from django.views.generic import ListView
from rest_framework.generics import ListAPIView

from data.common.permission import IsAuthenticatedUserType
from data.specialization.models import Specialization
from data.specialization.serializers import SpecializationSerializer


class SpecializationListAPIView(ListAPIView):
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [IsAuthenticatedUserType]
