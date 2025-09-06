from django.contrib import admin

from data.faculty.models import Faculty


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'id',
        'source_file',
    )


