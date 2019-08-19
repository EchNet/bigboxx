from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework import views, generics
from rest_framework_jwt.settings import api_settings

import logging

from api.permissions import BasePermission

logger = logging.getLogger(__name__)


class ValidateBoxDefinition(views.APIView):
  """
  """
  permission_classes = (BasePermission, )

  def post(self, request):
    response_payload = {}
    response_payload['token'] = self.get_token(user)
    return Response(response_payload)
