from django.urls import path
from data.file.views import *

urlpatterns = [
    path("excel/", ImportHistoryAPIView.as_view(), name="files"),
    path("files/upload/", FileUploadApiView.as_view(), name="file-upload"),
    path("files/<int:pk>/download/", ContractDownloadApiView.as_view(), name="file-download"),
]
