from django.urls import path
from rest_framework.routers import DefaultRouter
from data.student.views import (
    PhoneNumberViewSet,
    StudentEduYearListApiView,
    StudentEduYearExcelExportApiView,
    StudentDetailApiView,
    StudentStatisticsApiView,
    StatisticsExcelApiView,
    FacultyStatsAPIView,
    SendSmsView,
)

router = DefaultRouter()
router.register(r"number", PhoneNumberViewSet)
urlpatterns = [
                  path("year/<int:edu_year>/", StudentEduYearListApiView.as_view(), name="students-by-year"),
                  path('year/<int:edu_year>/export/', StudentEduYearExcelExportApiView.as_view(),
                       name='students-excel-export'),
                  path("<int:pk>/", StudentDetailApiView.as_view(), name="student-detail"),
                  path("statistics/<int:edu_year>/", StudentStatisticsApiView.as_view(), name="student-statistics"),
                  path("statistics/<int:edu_year>/report/", StatisticsExcelApiView.as_view(),
                       name="student-statistics-report"),
                  path("statistics/faculty/<int:edu_year>/", FacultyStatsAPIView.as_view()),
                  path("send-sms/", SendSmsView.as_view(), name="send-sms"),
              ] + router.urls
