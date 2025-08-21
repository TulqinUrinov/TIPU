from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from data.user.models import AdminUser
from data.user.serializers import AdminUserSerializer, AdminUserLoginSerializer
from data.common.permission import IsAuthenticatedUserType


class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = AdminUser.objects.filter(is_archived=False)
    serializer_class = AdminUserSerializer

    def perform_destroy(self, instance):
        # O'chirish o'rniga soft delete qilish
        instance.soft_delete()


class AdminUserLoginAPIView(APIView):
    def post(self, request):
        serializer = AdminUserLoginSerializer(data=request.data)

        if serializer.is_valid():
            admin_user = serializer.validated_data['user']

            if admin_user.is_archived:
                return Response({
                    'success': False,
                    'error': 'Hisobingiz bloklangan'
                }, status=status.HTTP_403_FORBIDDEN)

            # JWT token yaratish
            refresh = RefreshToken.for_user(admin_user)
            refresh['role'] = 'ADMIN'
            refresh['admin_user_id'] = str(admin_user.id)

            # Tokenlarni qaytarish
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


class MeAPIView(APIView):
    permission_classes = [IsAuthenticatedUserType]

    def get(self, request):
        admin_user = getattr(request, 'admin_user', None)
        if not admin_user:
            return Response({"error": "Admin user not found"}, status=403)

        serializer = AdminUserSerializer(admin_user)
        return Response(serializer.data)
