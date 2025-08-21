from django.contrib import admin
from django.contrib.auth.hashers import make_password

from data.user.models import AdminUser


@admin.register(AdminUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "is_archived", "created_at")
    search_fields = ("full_name", "phone_number")

    def save_model(self, request, obj, form, change):
        # Agar parol hashlanmagan bo‘lsa, avtomatik hash qilamiz
        if obj.password and not obj.password.startswith("pbkdf2_"):
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)
