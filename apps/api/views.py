from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404, JsonResponse
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views, generics
from rest_framework_jwt.settings import api_settings

from datetime import datetime
import logging

from api.permissions import BasePermissions

logger = logging.getLogger(__name__)


class FirstView(views.APIView):
  """
  """
  permission_classes = (BasePermission, )

  def get(self, request):
    response_payload = {}
    response_payload['token'] = self.get_token(user)
    return Response(response_payload)

  @staticmethod
  def get_token(user):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)
    #Allows token refresh
    if api_settings.JWT_ALLOW_REFRESH:
      payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())
    return jwt_encode_handler(payload),
