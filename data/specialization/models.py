from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.faculty.models import Faculty
    from data.file.models import Files


class Specialization(BaseModel):
    code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Mutaxassislik kodi"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Mutaxassislik nomi"
    )

    faculty: "Faculty" = models.ForeignKey(
        "faculty.Faculty",
        on_delete=models.CASCADE,
        related_name="specializations"
    )

    source_file: "Files" = models.ForeignKey(
        "file.Files",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="specializations"
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
