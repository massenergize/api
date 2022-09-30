# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Task


# @receiver(post_save, sender=Task)
# def create_or_update_periodic_task(sender, instance, created, **kwargs):
#     if created:
#         instance.create_task()