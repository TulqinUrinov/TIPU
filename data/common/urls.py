from django.urls import path
from .views import ImportStudentsAPIView, ImportPaymentsAPIView, StudentPhoneUploadAPIView

urlpatterns = [
    path('students/', ImportStudentsAPIView.as_view(), name='import-students'),
    path('payments/', ImportPaymentsAPIView.as_view(), name='import-payments'),
    path('phones/', StudentPhoneUploadAPIView.as_view(), name='import-phones'),
]
