from django.urls import path
from .views import ImportStudentsAPIView, ImportPaymentsAPIView

urlpatterns = [
    path('students/', ImportStudentsAPIView.as_view(), name='import-students'),
    path('payments/', ImportPaymentsAPIView.as_view(), name='import-payments'),
]
