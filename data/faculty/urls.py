from rest_framework.routers import DefaultRouter

from data.faculty.views import FacultyViewSet

router = DefaultRouter()

router.register(r"", FacultyViewSet)

urlpatterns = router.urls

