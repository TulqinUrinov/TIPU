import jwt
from django.conf import settings
from django.http import JsonResponse
from data.user.models import AdminUser
from data.student_account.models import StudentUser


class CustomJWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get("Authorization")

        request.admin_user = None
        request.student_user = None
        request.role = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                role = payload.get("role")

                if role == "ADMIN":
                    admin_id = payload.get("admin_user_id")
                    request.admin_user = AdminUser.objects.filter(id=admin_id).first()
                    request.role = "ADMIN"

                elif role == "STUDENT":
                    student_id = payload.get("student_user_id")
                    request.student_user = StudentUser.objects.filter(id=student_id).first()
                    request.role = "STUDENT"

            except jwt.ExpiredSignatureError:
                return JsonResponse({"error": "Token expired"}, status=401)
            except jwt.DecodeError:
                return JsonResponse({"error": "Invalid token"}, status=401)

        return self.get_response(request)
