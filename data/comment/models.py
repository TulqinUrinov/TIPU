from django.db import models
from typing import TYPE_CHECKING
from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.student.models import Student
    from data.user.models import AdminUser


class Comment(BaseModel):
    student:"Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    user:"AdminUser" = models.ForeignKey(
        "user.AdminUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    message:str = models.TextField(null=True, blank=True)
