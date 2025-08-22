from django.db import models

from data.common.models import BaseModel


class EducationYear(BaseModel):
    edu_year = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.edu_year
