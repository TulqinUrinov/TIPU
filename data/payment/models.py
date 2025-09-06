from django.db import models
from typing import TYPE_CHECKING

from django.db.models import JSONField

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.student.models import Student
    from data.user.models import AdminUser
    from data.file.models import Files


class Payment(BaseModel):
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="payments",
        to_field="jshshir",  # JSHSHIR bo'yicha bog'lash
        db_column="jshshir"  # Ma'lumotlar bazasida ustun nomi
    )

    source_file: "Files" = models.ForeignKey(
        "file.Files",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments"
    )

    contract_number = models.CharField(
        max_length=50,
        verbose_name="Shartnoma raqami"
    )

    payment_id = models.CharField(
        max_length=100,
        verbose_name="To'lov ID",
        unique=True
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="To'lov summasi"
    )

    payment_date = models.DateTimeField(verbose_name="To'lov sanasi")
    purpose = models.TextField(verbose_name="To'lov maqsadi")


class InstallmentPayment(BaseModel):
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        related_name="contract_payments"
    )
    installment_count = models.PositiveIntegerField(default=4)
    installment_payments = JSONField(default=list)  # bu yerda hamma splits saqlanadi

    left = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    custom = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.installment_count} parts"


# Sms
class ReminderConfig(models.Model):
    days_before = models.PositiveIntegerField(help_text="Qancha kun oldin sms yuboriladi")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Payment reminder config"
        verbose_name_plural = "Payment reminder configs"

    def __str__(self):
        return f"{self.days_before} kun oldin"


class ActionHistory(BaseModel):
    action_choices = (
        ("PAYMENT_CREATED", "Payment created"),
        ("PAYMENT_CANCELED", "Payment canceled"),
        ("INSTALLMENT_UPDATED", "Installment updates"),
    )

    student: "Student" = models.ForeignKey("student.Student", on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=50, choices=action_choices)
    description = models.TextField()
    canceled_by: "AdminUser" = models.ForeignKey(
        "user.AdminUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
