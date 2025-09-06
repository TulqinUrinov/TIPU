from django.db import models

from data.common.models import BaseModel
from data.file.models import Files


class Faculty(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Fakultet nomi")

    source_file: "Files" = models.ForeignKey(
        "file.Files",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faculties"
    )

    def __str__(self):
        return self.name
