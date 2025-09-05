from django.contrib import admin

from data.account.models import StudentUser, SmsVerification


@admin.register(StudentUser)
class StudentUserAdmin(admin.ModelAdmin):
    list_display = (
        'get_full_name',
        'phone_number',
        'get_jshshir',
    )

    def get_full_name(self, obj: StudentUser) -> str:
        return obj.student.full_name

    def get_jshshir(self, obj: StudentUser) -> int:
        return obj.student.jshshir


@admin.register(SmsVerification)
class SmsVerificationAdmin(admin.ModelAdmin):
    list_display = (
        'phone_number',
        'code',
        'expires_at',
    )
