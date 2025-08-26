from django.urls import path

from data.faculty.views import FacultyListAPIView

urlpatterns = [
    path('list/', FacultyListAPIView.as_view(), name='faculty-list'),
]
