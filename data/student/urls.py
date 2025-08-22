from django.urls import path

from data.student.views import StudentEduYearListApiView

urlpatterns = [
    path("year/<int:edu_year>/", StudentEduYearListApiView.as_view(), name="students-by-year"),
]
