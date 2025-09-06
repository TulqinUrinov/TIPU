from django.contrib import admin

from data.student.models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'id',
        'jshshir',
        'phone_number',
        'source_file',
        'specialization',
        'course',
        'education_type',
        'education_form',
        'group',
        'status',

    )

    search_fields = (
        'full_name',
        'jshshir',
        'phone_number'
    )
    list_filter = (
        'specialization',
        'course',
        'status',
    )
