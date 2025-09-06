from django.db import models
from typing import TYPE_CHECKING
from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.user.models import AdminUser
    from data.student.models import Student


class Files(BaseModel):
    FILE_TYPES = (
        ("EXCEL", "Excel"),
        ("HEMIS", "Hemis shartnoma shabloni"),
        ("MUQOBIL", "Muqobil to‘lov shartnoma shabloni"),
    )

    file_type = models.CharField(
        max_length=100,
        choices=FILE_TYPES,
        default="EXCEL"
    )
    file = models.FileField(upload_to='files')
    uploaded_by: "AdminUser" = models.ForeignKey(
        "user.AdminUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.file.name


class ContractFiles(BaseModel):
    file = models.FileField(upload_to='ContractFiles')
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.student.full_name} shartnomasi"


class FileDeleteHistory(BaseModel):
    file = models.ForeignKey(
        "file.Files",
        on_delete=models.CASCADE,
        related_name="delete_history"
    )
    deleted_by: "AdminUser" = models.ForeignKey(
        "user.AdminUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    deleted_data_count = models.JSONField(
        default=dict,
        help_text="O'chirilgan ma'lumotlar soni (students, contracts, payments)"
    )
    reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.file} - {self.deleted_by}"