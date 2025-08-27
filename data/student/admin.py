from django.contrib import admin

from data.student.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'id',
        'jshshir',
        'phone_number',
        'specialization',
        'course',
        'education_type',
        'education_form',
        'group',

    )

    search_fields = (
        'full_name',
        'jshshir',
        'phone_number'
    )
