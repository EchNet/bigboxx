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
        "name",
        "details",
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
        "name",
        "details",
        "size",
        "amount_in",
    )


class BoxDefinitionSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "name",
        "details",
        "size",
        "amount_in",
        "outcomes",
    )

  outcomes = OutcomeSerializer(many=True)


class BoxDefinitionListingSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "name",
    )


class BoxDefinitionServiceSerializer(serializers.Serializer):
  box_definition = BoxDefinitionWithoutOutcomesSerializer()
  outcomes = OutcomeServiceSerializer(many=True)
  hit_rate = serializers.FloatField()
  average_return = serializers.FloatField()
