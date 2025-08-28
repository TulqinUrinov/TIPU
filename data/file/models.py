from django.db import models

from data.common.models import BaseModel
from data.user.models import AdminUser


class Files(BaseModel):
    file = models.FileField(upload_to='files')
    uploaded_by: "AdminUser" = models.ForeignKey(
        "user.AdminUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.uploaded_by.full_name
