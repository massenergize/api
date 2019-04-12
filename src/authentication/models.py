from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

# Create your models here.
class EnergizeUser(models.Model):
  user = models.ForeignKey(User)
  profile = JSONField()

  def __str__(self):
    return self.user.get_full_name()
