from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from api.models import (ApiKey, BoxDefinition, Outcome)
from api.services import (BoxDefinitionService, OutcomeService)


# Outcome
class OutcomeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Outcome
    fields = (
        "title",
        "description",
        "probability",
        "amount_out",
    )


class OutcomeServiceSerializer(serializers.Serializer):
  outcome = OutcomeSerializer()
  hit_rate = serializers.FloatField()
  average_return = serializers.FloatField()


# BoxDefinition
class BoxDefinitionWithoutOutcomesSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "title",
        "description",
        "size",
        "amount_in",
    )


class BoxDefinitionSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "title",
        "description",
        "size",
        "amount_in",
        "outcomes",
        "in_service",
    )

  outcomes = OutcomeSerializer(many=True)
  in_service = serializers.SerializerMethodField()

  def get_in_service(self, obj):
    return BoxDefinitionService(obj).in_service


class BoxDefinitionListingSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "title",
    )


class BoxDefinitionServiceSerializer(serializers.Serializer):
  box_definition = BoxDefinitionWithoutOutcomesSerializer()
  outcomes = OutcomeServiceSerializer(many=True)
  hit_rate = serializers.FloatField()
  average_return = serializers.FloatField()
