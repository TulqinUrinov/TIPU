from django.urls import path
from data.file.views import *

urlpatterns = [
    path("excel/", ImportHistoryAPIView.as_view(), name="files"),
    path("upload/", FileUploadApiView.as_view(), name="file-upload"),
    path("contract/<int:pk>/download/", ContractDownloadApiView.as_view(), name="contract-download"),
]
