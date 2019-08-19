import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)


class BasePermission(permissions.BasePermission):
  """
  """

  def has_object_permission(self, request, view, obj):
    return True
