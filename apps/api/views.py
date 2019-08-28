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
import api.serializers as serializers

logger = logging.getLogger(__name__)


class BaseApiView(views.APIView):
  permission_classes = (ApiKeyPermission, )
  class Meta:
    methods = {}

  def handle_request(request):
    try:
      logger.info(f"{self.__class__.__name__} {request.method} subscriber={request.subscriber} input={request.input}")
      action = getattr(self, f"{request.method.lower()}_action")
      data = action(self, request.subscriber, request.input)
      method_descriptor = self.Meta.methods[request.method]
      response_status = method_descriptor.get("ok_response_status", status.HTTP_200_OK)
      many = method_descriptor.get("many", False)
      serializer = method_descriptor.get("serializer", serializers.BoxDefinitionSerializer)
      response_payload = { "data": serializer(data, many=many).data }
      logger.info(response_payload)
    except ValidationError as e:
      response_payload = {
          "message": "Invalid request.",
          "errors": ve.args,
      }
      response_status = status.HTTP_400_BAD_REQUEST
    except Http404:
      response_payload = {
          "message": "Not found.",
      }
      response_status = status.HTTP_404_NOT_FOUND
    except Exception as e:
      logger.error(e)
      response_payload = {"details": str(e)}
      response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    return Response(response_payload, response_status)

  def post(self, request):
    return self.handle_request(request) if "POST" in self.Meta.methods else super().post(request)

  def get(self, request):
    return self.handle_request(request) if "GET" in self.Meta.methods else super().get(request)


class ValidateBoxDefinitionView(BaseApiView):
  class Meta:
    methods = {
      "POST": {}
    }

  def post_action(self, subscriber, input):
    return BoxDefinitionService(BoxDefinitionOperations(**input).validate())


class CreateOrListBoxDefinitionView(BaseApiView):
  class Meta:
    methods = {
      "GET": {
        "serializer": serializers.BoxDefinitionListingSerializer,
        "many": True,
      }
      "POST": {
        "ok_response_status": status.HTTP_201_CREATED,
      }
    }

  def post_action(self, subscriber, input):
    return BoxDefinitionOperations(**input).build(subscriber)

  def get_action(self, subscriber, input):
    return BoxDefinition.objects.filter(subscriber=subscriber).all()


class RetrieveBoxDefinitionView(BaseApiView):
  class Meta:
    methods = {
      "GET": {
      }
    }

  def get_action(self, subscriber, input):
    pk = self.kwargs.get("pk", "")
    try:
      return BoxDefinition.objects.filter(subscriber=subscriber, pk=pk).get()
    except BoxDefinition.DoesNotExist:
      raise Http404()


class ClaimOutcomeView(views.APIView):
  serializer = serializers.OutcomeSerializer

  def action(self, subscriber, input):
    return SubscriberOperations(subscriber).claim_outcome(**input)
