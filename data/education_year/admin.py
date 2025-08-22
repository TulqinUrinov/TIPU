from django.contrib import admin

from data.education_year.models import EducationYear


@admin.register(EducationYear)
class EducationYearAdmin(admin.ModelAdmin):
    list_display = ('edu_year','id')
