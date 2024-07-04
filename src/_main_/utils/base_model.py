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


class CustomMeta(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        # Extract fields_to_translate from Meta and remove it
        meta_attrs = attrs.get('Meta', None)
        if hasattr(meta_attrs, 'fields_to_translate'):
            translatable_fields = meta_attrs.fields_to_translate
            delattr(meta_attrs, 'fields_to_translate')
        else:
            translatable_fields = []

        # Create the new class without fields_to_translate in Meta
        new_class = super().__new__(cls, name, bases, attrs)

        # Inject fields_to_translate directly into the class
        setattr(new_class, 'fields_to_translate', translatable_fields)

        return new_class