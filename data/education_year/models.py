from django.db import models

from data.common.models import BaseModel


class EducationYear(BaseModel):
    year = models.CharField(max_length=20, null=True, blank=True)
