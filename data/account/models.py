from django.contrib.auth.hashers import make_password, check_password

from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.student.models import Student

from data.common.models import BaseModel


class StudentUser(BaseModel):
    student: "Student" = models.OneToOneField(
        'student.Student',
        on_delete=models.CASCADE,
        related_name='user_account'
    )
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Telefon raqami")
    password = models.CharField(max_length=128, verbose_name="Parol")

    def __str__(self):
        return f"{self.student.full_name} - {self.phone_number}"

    def set_password(self, raw_password):
        """Parolni hash qiladi."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Parolni tekshiradi."""
        return check_password(raw_password, self.password)

    def soft_delete(self):
        """StudentUserni soft delete qiladi."""
        super().soft_delete()
        # Qo'shimcha logika kerak bo'lsa
        # Masalan, student bilan bog'liq barcha aktiv sessionlarni yopish

    def restore(self):
        """StudentUserni qayta tiklaydi."""
        super().restore()
        # Qo'shimcha logika kerak bo'lsa
