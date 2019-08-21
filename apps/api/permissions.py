import logging
from rest_framework import permissions

from api.models import ApiKey

logger = logging.getLogger(__name__)


class ApiKeyPermission(permissions.BasePermission):
  def has_permission(self, request, view):
    api_key = request.META.get("HTTP_X_API_KEY")
    if not api_key:
      logger.debug("Missing API key")
      return False

    api_key_obj = ApiKey.objects.filter(api_key=api_key).first()
    if not api_key_obj:
      logger.info(f"API key {api_key} invalid")
      return False
    if api_key_obj.deactivated:
      logger.warn(f"API key {api_key} deactivated")
      return False

    request.subscriber = api_key_obj.subscriber
    logger.info(f"API key key={api_key} subscriber={request.subscriber}")
    return True
