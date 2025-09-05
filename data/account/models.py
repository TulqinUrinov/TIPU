import datetime
import random

from django.contrib.auth.hashers import make_password, check_password

from django.db import models
from typing import TYPE_CHECKING

from django.utils import timezone

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


class SmsVerification(BaseModel):
    phone_number = models.CharField(max_length=15, unique=True)
    jshshir = models.CharField(max_length=14, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)

    code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    # yangi field
    resend_available_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = str(random.randint(100000, 999999))
            self.expires_at = timezone.now() + datetime.timedelta(minutes=5)
            self.resend_available_at = timezone.now() + datetime.timedelta(seconds=60)
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def can_resend(self):
        """Qayta yuborish mumkinmi"""
        return timezone.now() >= self.resend_available_at

    def seconds_left_for_resend(self):
        """Qolgan sekundlarni qaytaradi"""
        if self.can_resend():
            return 0
        delta = self.resend_available_at - timezone.now()
        return int(delta.total_seconds())

# class SmsVerification(BaseModel):
#     phone_number = models.CharField(max_length=15, unique=True)
#     jshshir = models.CharField(max_length=14, null=True, blank=True)
#     password = models.CharField(max_length=128, null=True, blank=True)
#
#     code = models.CharField(max_length=6)
#     is_verified = models.BooleanField(default=False)
#     expires_at = models.DateTimeField()
#
#     def save(self, *args, **kwargs):
#         if not self.id:
#             self.code = str(random.randint(100000, 999999))
#             self.expires_at = timezone.now() + datetime.timedelta(minutes=5)
#         super().save(*args, **kwargs)
#
#     def is_expired(self):
#         return timezone.now() > self.expires_at
