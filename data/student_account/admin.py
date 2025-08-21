from django.contrib import admin

from data.student_account.models import StudentUser


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
