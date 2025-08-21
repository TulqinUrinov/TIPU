from rest_framework.routers import DefaultRouter
from django.urls import path

from data.user.views import AdminUserViewSet, AdminUserLoginAPIView, JWTtokenRefresh, MeAPIView

router = DefaultRouter()
router.register(r"", AdminUserViewSet)

urlpatterns = [
                  path("login/", AdminUserLoginAPIView.as_view(), name='user-login'),
                  path("refresh/", JWTtokenRefresh.as_view(), name='token-refresh'),
                  path("me/", MeAPIView.as_view(), name='user-me'),
              ] + router.urls
