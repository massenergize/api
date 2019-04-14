from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

# Create your models here.
class UserProfile(models.Model):
  user = models.ForeignKey(User)
  photo = models.ImageField()
  info = JSONField()

  def __str__(self):
    return self.user.get_full_name()
