from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework import views, generics
from rest_framework_jwt.settings import api_settings

import logging

from api.models import Subscriber
from api.operations import BoxDefinitionOperations
from api.permissions import BasePermission
from api.serializers import BoxDefinitionSerializer

logger = logging.getLogger(__name__)


class ValidateBoxDefinition(views.APIView):
  """
  """
  permission_classes = (BasePermission, )

  def post(self, request):
    input = request.data
    logger.info("ValidateBoxDefinition")
    try:
      subscriber = Subscriber.objects.all().first()
      if not subscriber:
        subscriber = Subscriber(name="TEST")
        subscriber.save()

      box_definition = BoxDefinitionOperations(subscriber, **input).validate()

      response_payload = {"box_definition": BoxDefinitionSerializer(box_definition).data}
      response_status = status.HTTP_200_OK
    except ValidationError as ve:
      response_payload = {
          "details": "Invalid box definition.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except ValueError as e:
      response_payload = {"details": str(e)}
      response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(response_payload, response_status)
