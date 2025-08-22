from django.contrib import admin

from data.studentedu_year.models import StudentEduYear


@admin.register(StudentEduYear)
class StudentEduYearAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'education_year',
    )

    # student orqali bog'langan modeldan qidirish
    search_fields = (
        'student__full_name',
        'student__jshshir',
    )
