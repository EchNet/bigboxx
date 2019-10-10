from rest_framework import serializers

from api.models import (BoxDefinition, Card, Outcome)


def get_outcome_hit_rate(outcome):
  return outcome.probability / outcome.box_definition.size


def get_outcome_average_return(outcome):
  return get_outcome_hit_rate(outcome) * outcome.amount_out / outcome.box_definition.amount_in


# Outcome
class OutcomeSerializer(serializers.ModelSerializer):
  class Meta:
    model = Outcome
    fields = (
        "name",
        "details",
        "probability",
        "amount_out",
        "hit_rate",
        "average_return",
    )

  hit_rate = serializers.SerializerMethodField()
  average_return = serializers.SerializerMethodField()

  def get_hit_rate(self, outcome):
    return get_outcome_hit_rate(outcome)

  def get_average_return(self, outcome):
    return get_outcome_average_return(outcome)


# Card
class CardSerializer(serializers.ModelSerializer):
  class Meta:
    model = Card
    fields = (
        "box_id",
        "outcome",
        "sequence",
        "user_token",
        "consumed",
    )

  outcome = OutcomeSerializer()


# BoxDefinition (listing format)
class BoxDefinitionListingSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = (
        "id",
        "name",
    )


# BoxDefinition
class BoxDefinitionSerializer(serializers.ModelSerializer):
  class Meta:
    model = BoxDefinition
    fields = ("id", "name", "details", "size", "amount_in", "outcomes", "hit_rate",
              "average_return")

  outcomes = OutcomeSerializer(many=True)
  hit_rate = serializers.SerializerMethodField()
  average_return = serializers.SerializerMethodField()

  def get_hit_rate(self, box_definition):
    return sum(outcome.probability for outcome in box_definition.outcomes) / box_definition.size

  def get_average_return(self, box_definition):
    return sum(get_outcome_average_return(outcome) for outcome in box_definition.outcomes)
