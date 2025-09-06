from django.urls import path
from rest_framework.routers import DefaultRouter

from data.file.views import FileViewSet, ImportHistoryAPIView, ContractDownloadApiView, SpecialDocsListApiView, \
    FileDeleteAPIView, FileDeleteHistoryListAPIView

router = DefaultRouter()
router.register(r"", FileViewSet, basename="file")

urlpatterns = [
    path("excel/", ImportHistoryAPIView.as_view(), name="files"),
    path("contract/<int:pk>/download/", ContractDownloadApiView.as_view(), name="contract-download"),
    path("docx/", SpecialDocsListApiView.as_view(), name='docs'),
    path("delete/<int:file_id>/", FileDeleteAPIView.as_view()),
    path("history/", FileDeleteHistoryListAPIView.as_view()),
]

urlpatterns += router.urls
