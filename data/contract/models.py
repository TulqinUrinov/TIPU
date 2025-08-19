from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.student.models import Student


class Contract(BaseModel):
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="contracts"
    )

    contract_type = models.CharField(
        max_length=100,
        verbose_name="Shartnoma shakli"
    )  # uch tomonlama, ikki tomonlama

    initial_balance_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr boshiga qoldiq (DT)",
        default=0
    )

    initial_balance_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr boshiga qoldiq (KT)",
        default=0
    )

    period_amount_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr uchun aylanma (DT)",
        default=0
    )

    returned_amount_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Qaytarilgan summa (DT)",
        default=0
    )

    paid_amount_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="To'langan summa (KT)",
        default=0
    )

    final_balance_dt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr ohiriga qoldiq (DT)",
        default=0
    )

    final_balance_kt = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Davr ohiriga qoldiq (KT)",
        default=0
    )

    payment_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="To'langan summa foizda",
        default=0
    )

    def __str__(self):
        return f"{self.student.full_name} - {self.contract_type}"
