from django.contrib import admin

from data.student.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'jshshir',
        'specialization',
        'course',
        'education_type',
        'education_form',
        'group',

    )
