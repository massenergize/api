from django.db import models
import uuid



class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # to store any extra meta data
    info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.id)

    def to_json(self, full=False, tiny_info=False):
        return {
            "id": str(self.pk),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "info": self.info
        }

    class Meta:
        abstract = True
