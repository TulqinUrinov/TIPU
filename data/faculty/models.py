from django.db import models

from data.common.models import BaseModel


class Faculty(BaseModel):
    name = models.CharField(max_length=255, verbose_name="Fakultet nomi")

    def __str__(self):
        return self.name
