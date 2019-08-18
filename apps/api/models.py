from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ApiKey(models.Model):
  """
  API keys may be entered manually through the Django Admin UI
  """

  # Subscriber names must be all alphanumeric.
  subscriber_name = models.CharField(
      blank=False, max_length=255, null=False, db_index=True, verbose_name=_("subscriber name"))

  # API keys are random ASCII strings.
  api_key = models.CharField(blank=False, max_length=255, null=False, verbose_name=_("API key"))

  @staticmethod
  def get(subscriber_name):
    obj = ApiKey.objects.filter(subscriber_name=subscriber_name).first()
    if not obj and settings.DEBUG:
      return "XYXYXYXYXYXY"  # Don't fail in dev mode.
    return obj.api_key if obj else None
