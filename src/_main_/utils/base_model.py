from django.db import models
import uuid

class RootModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    # to store any extra meta data
    info = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.pk)

    def to_json(self, full=False, tiny_info=False):
        return {
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "info": self.info
        }

    class Meta:
        abstract = True

class BaseModel(RootModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id)

    def to_json(self, full=False, tiny_info=False):
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_deleted": self.is_deleted,
            "info": self.info
        }

    class Meta:
        abstract = True
        
        
class Faq(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    
    def __str__(self):
        return self.question
    
    def to_json(self):
        return {
            "id": str(self.id),
            "question": self.question,
            "answer": self.answer
        }
    
    class Meta:
        verbose_name_plural = "FAQs"
        abstract = True
        