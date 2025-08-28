from rest_framework.generics import ListAPIView

from data.common.permission import IsAuthenticatedUserType
from data.file.models import Files
from data.file.serializers import FileSerializer


class ImportHistoryAPIView(ListAPIView):
    permission_classes = [IsAuthenticatedUserType]
    queryset = Files.objects.all().order_by("-created_at")
    serializer_class = FileSerializer
