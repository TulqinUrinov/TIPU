from django.urls import path
from data.account.views import (
    JWTtokenRefresh,
    StudentUserLoginAPIView,
    SendSmsCodeAPIView,
    VerifySmsAndRegisterAPIView,
    StudentUserPasswordUpdateAPIView,
    StudentMeAPIView,
    ResendSmsCodeAPIView,
    ForgotPasswordSendSmsAPIView,
    ForgotPasswordVerifyAPIView,
)

urlpatterns = [
    path('login/', StudentUserLoginAPIView.as_view(), name="student-login"),
    path("send-sms/", SendSmsCodeAPIView.as_view(), name="send-sms"),
    path("register/", VerifySmsAndRegisterAPIView.as_view(), name="register"),
    path("resend-code/", ResendSmsCodeAPIView.as_view(), name="resend-sms-code"),
    path('password-update/', StudentUserPasswordUpdateAPIView.as_view(), name='student-password-update'),
    path('token/refresh/', JWTtokenRefresh.as_view(), name='token-refresh'),
    path('me/', StudentMeAPIView.as_view(), name='student-me'),
    path("forgot-password/send-sms/", ForgotPasswordSendSmsAPIView.as_view(), name="forgot-password-send-sms"),
    path("forgot-password/verify/", ForgotPasswordVerifyAPIView.as_view(), name="forgot-password-verify"),
]
