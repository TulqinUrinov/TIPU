from django.urls import path
from data.account.views import *

urlpatterns = [
    path('login/', StudentUserLoginAPIView.as_view(), name="student-login"),
    path('register/', StudentUserRegisterAPIView.as_view(), name='student-register'),
    path('token/refresh/', JWTtokenRefresh.as_view(), name='token-refresh'),
    path('me/', StudentMeAPIView.as_view(), name='student-me'),
]
