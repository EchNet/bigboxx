from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import BoxDefinition
from api.tasks import run_prepare_box_service


@receiver(post_save, sender=BoxDefinition)
def user_saved_callback(sender, instance, created, **kwargs):
  if created and not settings.TESTING:
    run_prepare_box_service(instance.id)
