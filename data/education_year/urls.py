from rest_framework import routers

from data.education_year.views import EducationYearViewSet

router = routers.DefaultRouter()
router.register(r"", EducationYearViewSet)

urlpatterns = router.urls
