from multiprocessing.resource_tracker import register

from django.contrib import admin

from data.file.models import Files, ContractFiles


@admin.register(Files)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "file",
        "file_type",
        "uploaded_by",
        "created_at",
    )


@admin.register(ContractFiles)
class ContractFilesAdmin(admin.ModelAdmin):
    list_display = (
        "file",
        "student",
    )