from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from api.models import (ApiKey, BoxDefinition, Outcome)


# ApiKey
class ApiKeySerializer(serializers.ModelSerializer):
  class Meta:
    model = ApiKey
    fields = (
        "subscriber_name",
        "api_key",
    )


# Outcome
class OutcomeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Outcome
    fields = (
        "title",
        "description",
        "probability",
        "amount_out",
        "hit_rate",
        "average_return",
    )


# BoxDefinition
class BoxDefinitionSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "title",
        "description",
        "log2size",
        "size",
        "amount_in",
        "hit_rate",
        "average_return",
        "outcomes",
    )

  outcomes = OutcomeSerializer(many=True)
