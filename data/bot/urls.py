from rest_framework.routers import DefaultRouter
from data.bot.views import TgPostViewSet

router = DefaultRouter()
router.register(r"", TgPostViewSet)

urlpatterns = router.urls
