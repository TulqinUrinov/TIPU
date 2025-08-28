from django.urls import path
from data.file.views import *

urlpatterns = [
    path("excel/", ImportHistoryAPIView.as_view(), name="files"),
]
