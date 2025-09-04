from django.urls import path

from data.specialization.views import SpecializationListAPIView

urlpatterns = [
    path('list/', SpecializationListAPIView.as_view(), name='list'),
]