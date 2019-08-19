from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from api.models import ApiKey, BoxDefinition


# ApiKey
class ApiKeySerializer(serializers.ModelSerializer):
  class Meta:
    model = ApiKey
    fields = (
        "subscriber_name",
        "api_key",
    )


# BoxDefinition
class BoxDefinitionSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "title",
        "description",
        "amount_in",
        "log2size",
    )
