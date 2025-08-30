from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from data.common.models import BaseModel


class AdminUser(BaseModel):
    full_name = models.CharField(max_length=100, verbose_name="F.I.O")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Telefon raqami")
    password = models.CharField(max_length=255, verbose_name="Parol")

    def __str__(self):
        return f"{self.full_name}"

    def set_password(self, raw_password):
        """Parolni hash qiladi."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Parolni tekshiradi."""
        return check_password(raw_password, self.password)

    def soft_delete(self):
        """Userni soft delete qiladi."""
        super().soft_delete()

    def restore(self):
        """Userni qayta tiklaydi."""
        super().restore()
