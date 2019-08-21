from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404, JsonResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework import views, generics
from rest_framework_jwt.settings import api_settings

import logging

from api.models import BoxDefinition, Subscriber
from api.operations import BoxDefinitionOperations
from api.permissions import ApiKeyPermission
from api.serializers import BoxDefinitionSerializer, BoxDefinitionListingSerializer

logger = logging.getLogger(__name__)


class BoxDefinitionsView(generics.CreateAPIView):
  queryset = BoxDefinition.objects.all()
  permission_classes = (ApiKeyPermission, )

  def create(self, request):
    try:
      logger.info("BoxDefinitionsView CREATE")
      subscriber = request.subscriber
      data = BoxDefinitionOperations(subscriber, **input).build()
      response_payload = {"data": BoxDefinitionSerializer(data).data}
      response_status = status.HTTP_201_CREATED
    except ValidationError as e:
      response_payload = {
          "details": "Invalid box definition.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except Exception as e:
      logger.error(e)
      response_payload = {"details": str(e)}
      response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response_payload, response_status)

  def get(self, request):
    try:
      logger.info("BoxDefinitionsView GET")
      subscriber = request.subscriber
      data = BoxDefinition.objects.filter(subscriber=subscriber).all()
      response_payload = {"data": BoxDefinitionListingSerializer(data, many=True).data}
      response_status = status.HTTP_201_CREATED
    except ValidationError as e:
      response_payload = {
          "details": "Invalid box definition.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except Exception as e:
      logger.error(e)
      response_payload = {"details": str(e)}
      response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response_payload, response_status)


class ValidateBoxDefinition(views.APIView):
  permission_classes = (ApiKeyPermission, )

  def post(self, request):
    input = request.data
    logger.info("ValidateBoxDefinition")
    try:
      subscriber = request.subscriber
      data = BoxDefinitionOperations(subscriber, **input).validate()
      response_payload = {"data": BoxDefinitionSerializer(data).data}
      response_status = status.HTTP_200_OK
    except ValidationError as ve:
      response_payload = {
          "details": "Invalid box definition.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except Exception as e:
      logger.error(e)
      response_payload = {"details": str(e)}
      response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response_payload, response_status)
