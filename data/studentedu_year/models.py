from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.student.models import Student
    from data.education_year.models import EducationYear
    from data.payment.models import Payment


class StudentEduYear(BaseModel):
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_years",
    )
    education_year: "EducationYear" = models.ForeignKey(
        "education_year.EducationYear",
        on_delete=models.CASCADE,
        related_name="student_years",
    )

    class Meta:
        unique_together = ("student", "education_year")  # bitta student bitta o‘quv yilida faqat 1 marta bo‘ladi

    def __str__(self):
        return f"{self.student.full_name} - {self.education_year.edu_year}"


# class PaymentEduYear(BaseModel):
#     payment: "Payment" = models.ForeignKey(
#         "payment.Payment",
#         on_delete=models.CASCADE,
#         related_name="payment_years",
#
#     )
#
#     education_year: "EducationYear" = models.ForeignKey(
#         "education_year.EducationYear",
#         on_delete=models.CASCADE,
#         related_name="student_years",
#     )
#
#     def __str__(self):
#         return f"{self.payment.student.full_name} - {self.education_year.edu_year}"
