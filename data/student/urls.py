from django.urls import path

from data.student.views import *

urlpatterns = [
    path("year/<int:edu_year>/", StudentEduYearListApiView.as_view(), name="students-by-year"),
    path("<int:pk>/", StudentGetApiView.as_view(), name="student-detail"),
]
