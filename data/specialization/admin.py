from django.contrib import admin

from data.specialization.models import Specialization


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'faculty',
        'code',
        'source_file',
    )
