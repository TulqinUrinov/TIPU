from rest_framework import status

from rest_framework.response import Response
from rest_framework.views import APIView

from data.account.serializers import StudentUserLoginSerializer, StudentUserRegisterSerializer

from rest_framework_simplejwt.tokens import RefreshToken

from data.common.permission import IsAuthenticatedUserType


class StudentUserRegisterAPIView(APIView):
    def post(self, request):
        serializer = StudentUserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            student_user = serializer.save()

            # Registratsiyadan so'ng avtomatik token yaratish
            refresh = RefreshToken.for_user(student_user)
            refresh['role'] = 'STUDENT'
            refresh['student_user_id'] = str(student_user.id)

            # Access tokenga ham qo‘shish
            access = refresh.access_token
            access['role'] = 'STUDENT'
            access['student_user_id'] = str(student_user.id)

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class StudentUserLoginAPIView(APIView):
    def post(self, request):
        serializer = StudentUserLoginSerializer(data=request.data)

        if serializer.is_valid():
            student_user = serializer.validated_data['student_user']

            if student_user.is_archived:
                return Response({
                    'success': False,
                    'error': 'Hisobingiz bloklangan'
                }, status=status.HTTP_403_FORBIDDEN)

            # JWT token yaratish
            refresh = RefreshToken.for_user(student_user)
            refresh['role'] = 'STUDENT'
            refresh['student_user_id'] = str(student_user.id)

            return Response({
                'access': str(refresh.access_token),
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
        print(student_user)
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
