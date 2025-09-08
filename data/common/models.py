from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Qo'shimcha fieldlar
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        """Obyektni soft delete qiladi."""
        self.is_archived = True
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Soft delete qilingan obyektni qayta tiklaydi."""
        self.is_archived = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True
