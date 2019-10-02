import logging

from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseNotAllowed
from rest_framework import status
from rest_framework.response import Response
from rest_framework import views

from api.models import BoxDefinition
from api.operations import (BoxDefinitionOperations, SubscriberOperations)
import api.permissions as permissions
import api.serializers as serializers
from api.services import BoxDefinitionService

logger = logging.getLogger(__name__)


class BaseApiView(views.APIView):
  permission_classes = (permissions.ApiKeyPermission, )

  class Meta:
    methods = {}

  def handle_request(self, request):
    try:
      logger.info(
          f"{self.__class__.__name__} {request.method} subscriber={request.subscriber} input={request.data}"
      )
      action = getattr(self, f"do_{request.method.lower()}")
      data = action(request)
      method_descriptor = self.Meta.methods[request.method]
      response_status = method_descriptor.get("ok_response_status", status.HTTP_200_OK)
      many = method_descriptor.get("many", False)
      serializer = method_descriptor.get("serializer", serializers.BoxDefinitionSerializer)
      response_payload = {"data": serializer(data, many=many).data}
      logger.info(response_payload)
    except ValidationError as ve:
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
      raise e
    return Response(response_payload, response_status)

  def post(self, request, *args, **kwargs):
    if "POST" in self.Meta.methods:
      return self.handle_request(request)
    return HttpResponseNotAllowed(self.Meta.methods.keys())

  def get(self, request, *args, **kwargs):
    if "GET" in self.Meta.methods:
      return self.handle_request(request)
    return HttpResponseNotAllowed(self.Meta.methods.keys())


class CreateOrListBoxDefinitionView(BaseApiView):
  class Meta:
    methods = {
        "GET": {
            "serializer": serializers.BoxDefinitionListingSerializer,
            "many": True,
        },
        "POST": {
            "ok_response_status": status.HTTP_201_CREATED,
        }
    }

  def do_post(self, request):
    return BoxDefinitionOperations(**request.data).build()

  def do_get(self, request):
    return BoxDefinition.objects.all()


class BaseBoxDefinitionView(BaseApiView):
  def get_object(self, request):
    try:
      pk = self.kwargs.get("pk")
      return BoxDefinition.objects.filter(pk=pk).get()
    except BoxDefinition.DoesNotExist:
      raise Http404()


class RetrieveBoxDefinitionView(BaseBoxDefinitionView):
  class Meta:
    methods = {"GET": {}}

  def do_get(self, request):
    return self.get_object(request)


class ValidateBoxDefinitionView(BaseApiView):
  class Meta:
    methods = {
        "POST": {
            "serializer": serializers.BoxDefinitionServiceSerializer,
        }
    }

  def do_post(self, request):
    return BoxDefinitionService(BoxDefinitionOperations(**request.data).validate())


class ClaimOutcomeView(BaseBoxDefinitionView):
  class Meta:
    methods = {
        "POST": {
            "serializer": serializers.OutcomeSerializer,
        }
    }

  def do_post(self, request):
    box_definition = self.get_object(request)
    return SubscriberOperations(request.subscriber).claim_outcome(box_definition, **request.data)
