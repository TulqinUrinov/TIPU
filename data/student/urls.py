from django.urls import path

from data.student.views import *

urlpatterns = [
    path("year/<int:edu_year>/", StudentEduYearListApiView.as_view(), name="students-by-year"),
    path('year/<int:edu_year>/export/', StudentEduYearExcelExportApiView.as_view(), name='students-excel-export'),
    path("<int:pk>/", StudentDetailApiView.as_view(), name="student-detail"),
    path("statistics/<int:edu_year>/", StudentStatisticsApiView.as_view(), name="student-statistics"),
    path("statistics/<int:edu_year>/report/", StatisticsExcelApiView.as_view(), name="student-statistics-report"),
    path("statistics/faculty/<int:edu_year>/",FacultyStatsAPIView.as_view()),
    path("send-sms/", SendSmsView.as_view(), name="send-sms")
]
