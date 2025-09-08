import datetime
import random

from django.core.serializers import serialize
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from data.account.models import SmsVerification
from data.account.serializers import (
    StudentUserLoginSerializer,
    StudentUserPasswordUpdateSerializer,
    VerifySmsSerializer,
    SendSmsCodeSerializer, ForgotPasswordSendSmsSerializer, ForgotPasswordVerifySerializer,
)
from data.common.permission import IsAuthenticatedUserType
from sms import SayqalSms


class SendSmsCodeAPIView(APIView):
    def post(self, request):
        serializer = SendSmsCodeSerializer(data=request.data)
        if serializer.is_valid():
            sms = serializer.save()

            # SMS yuborish
            sms_service = SayqalSms()
            sms_service.send_sms(sms.phone_number, f"Sizning tasdiqlash kodingiz: {sms.code}")

            return Response({"phone_number": sms.phone_number, "message": "Tasdiqlash kodi yuborildi"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendSmsCodeAPIView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        try:
            sms = SmsVerification.objects.get(phone_number=phone_number, is_verified=False)
        except SmsVerification.DoesNotExist:
            return Response({"detail": "Bunday raqamga yuborilgan kod topilmadi"}, status=400)

        # Tekshiramiz: qayta yuborish mumkinmi?
        if not sms.can_resend():
            return Response(
                {
                    "detail": f"Qayta yuborish uchun {sms.seconds_left_for_resend()} soniya kuting"
                },
                status=400
            )

        # Yangi kod beramiz
        sms.code = str(random.randint(100000, 999999))
        sms.expires_at = timezone.now() + datetime.timedelta(minutes=5)
        sms.resend_available_at = timezone.now() + datetime.timedelta(seconds=120)
        sms.save()

        sms_service = SayqalSms()
        sms_service.send_sms(sms.phone_number, f"Sizning tasdiqlash kodingiz: {sms.code}")

        return Response({"message": "Yangi kod yuborildi"})


class VerifySmsAndRegisterAPIView(APIView):
    def post(self, request):
        serializer = VerifySmsSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # JWT token qaytarish
            refresh = RefreshToken.for_user(user)
            refresh['role'] = 'STUDENT'
            refresh['student_user_id'] = str(user.id)

            access = refresh.access_token
            access['role'] = 'STUDENT'
            access['student_user_id'] = str(user.id)

            return Response({
                "access": str(access),
                "refresh": str(refresh),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentUserLoginAPIView(APIView):
    def post(self, request):
        serializer = StudentUserLoginSerializer(data=request.data)

        if serializer.is_valid():
            student_user = serializer.validated_data['student_user']
            print(student_user.id)

            if student_user.is_archived:
                return Response({
                    'success': False,
                    'error': 'Hisobingiz bloklangan'
                }, status=status.HTTP_403_FORBIDDEN)

            # JWT token yaratish
            refresh = RefreshToken.for_user(student_user)
            refresh['role'] = 'STUDENT'
            refresh['student_user_id'] = str(student_user.id)

            # Access tokenga ham qo‘shish
            access = refresh.access_token
            access['role'] = 'STUDENT'
            access['student_user_id'] = str(student_user.id)

            return Response({
                'access': str(access),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class JWTtokenRefresh(APIView):
    """
    Refresh JWT token using refresh token.
    """

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            refresh = RefreshToken(refresh_token)
            access = refresh.access_token
            return Response(
                {"access": str(access), "refresh": str(refresh)},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class StudentMeAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def get(self, request):
        student_user = getattr(request, 'student_user', None)
        if not student_user:
            return Response({"error": "Student user not found"}, status=403)

        data = {
            'student_id': student_user.student.id,
            'full_name': student_user.student.full_name,
            'phone_number': student_user.phone_number,
            'jshshir': student_user.student.jshshir,
            'created_at': student_user.created_at
        }
        return Response(data)


# Parolni yangilash
class StudentUserPasswordUpdateAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def put(self, request):
        serializer = StudentUserPasswordUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "detail": "Parol muvaffaqiyatli yangilandi"},
                status=status.HTTP_200_OK
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class ForgotPasswordSendSmsAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSendSmsSerializer(data=request.data)
        if serializer.is_valid():
            sms = serializer.save()

            # SMS yuborish
            sms_service = SayqalSms()
            sms_service.send_sms(
                sms.phone_number,
                f"Parolni tiklash kodi: {sms.code}"
            )

            return Response({
                "detail": "Parolni tiklash uchun kod yuborildi",
                "phone_number": sms.phone_number,
                "jshshir": sms.jshshir
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordVerifyAPIView(APIView):
    def post(self, request):
        serializer = ForgotPasswordVerifySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Parol muvaffaqiyatli yangilandi"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class StudentUserRegisterAPIView(APIView):
#     def post(self, request):
#         serializer = StudentUserRegisterSerializer(data=request.data)
#
#         if serializer.is_valid():
#             student_user = serializer.save()
#             print(student_user.id)
#
#             # Registratsiyadan so'ng avtomatik token yaratish
#             refresh = RefreshToken.for_user(student_user)
#             refresh['role'] = 'STUDENT'
#             refresh['student_user_id'] = str(student_user.id)
#
#             # Access tokenga ham qo‘shish
#             access = refresh.access_token
#             access['role'] = 'STUDENT'
#             access['student_user_id'] = str(student_user.id)
#
#             return Response({
#                 'access': str(access),
#                 'refresh': str(refresh),
#             }, status=status.HTTP_201_CREATED)
#
#         return Response({
#             'success': False,
#             'errors': serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)
