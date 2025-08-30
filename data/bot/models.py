from django.db import models
from typing import TYPE_CHECKING

from data.common.models import BaseModel

if TYPE_CHECKING:
    from data.student.models import Student


class BotUser(BaseModel):
    chat_id = models.BigIntegerField(unique=True)

    username = models.CharField(max_length=50, null=True, blank=True)

    tg_name = models.CharField(max_length=100, null=True, blank=True)

    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )


class TgPost(BaseModel):
    message = models.TextField(verbose_name="Xabar matni")
    file = models.FileField(upload_to="tg_posts/", null=True, blank=True, verbose_name="Media (rasm/video)")

    def __str__(self):
        return f"TgPost #{self.id} - {self.message[:30]}"
