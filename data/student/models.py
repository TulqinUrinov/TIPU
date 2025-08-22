from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.specialization.models import Specialization


class Student(BaseModel):
    full_name = models.CharField(
        max_length=255,
        verbose_name="Talaba F.I.Sh"
    )

    jshshir = models.CharField(
        max_length=50,
        verbose_name="JSHSHIR",
        unique=True
    )

    status = models.CharField(
        max_length=50,
        verbose_name="Talaba statusi",
        default="O‘qimoqda"
    )

    specialization: "Specialization" = models.ForeignKey(
        "specialization.Specialization",
        on_delete=models.CASCADE,
        related_name="students"
    )

    course = models.CharField(
        max_length=50,
        verbose_name="Talaba kursi"
    )

    education_type = models.CharField(
        max_length=50,
        verbose_name="Taʼlim turi"
    )  # Bakalavr, Magistr

    education_form = models.CharField(
        max_length=50,
        verbose_name="Taʼlim shakli"
    )  # Sirtqi, Kunduzgi

    group = models.CharField(
        max_length=50,
        verbose_name="Gruhi"
    )

    def __str__(self):
        return self.full_name



