from rest_framework.permissions import BasePermission


class IsAuthenticatedUserType(BasePermission):
    """
    Requestdagi userni role asosida ajratadi.
    Middleware orqali request.admin_user yoki request.student_user o'rnatiladi.
    """

    def has_permission(self, request, view):
        if getattr(request, 'admin_user', None):
            return True
        if getattr(request, 'student_user', None):
            return True

        return False
