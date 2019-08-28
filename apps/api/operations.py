import logging
from django.core.validators import ValidationError

from api.models import (BoxDefinition, Outcome)
from api.services import BoxDefinitionService
from utils.validator import (FieldValidator, ItemValidator)

logger = logging.getLogger(__name__)

TITLE_FIELD_NAME = "title"
DESCRIPTION_FIELD_NAME = "description"
AMOUNT_IN_FIELD_NAME = "amount_in"
AMOUNT_OUT_FIELD_NAME = "amount_out"
LOG2_SIZE_FIELD_NAME = "log2size"
PROBABILITY_FIELD_NAME = "probability"
OUTCOMES_FIELD_NAME = "outcomes"

# Input validation constants.
MAX_TITLE_LENGTH = 50
MAX_DESCRIPTION_LENGTH = 250
MIN_LOG2_SIZE = 10
MAX_LOG2_SIZE = 29
MIN_OUTCOMES = 1
MAX_OUTCOMES = 1000


class BoxDefinitionOrOutcomeValidator(ItemValidator):
  def validate_title(self):
    self._expect(TITLE_FIELD_NAME) \
      .to_be_truthy() \
      .to_be_string() \
      .length_in_range(1, MAX_TITLE_LENGTH).keep()

  def validate_description(self):
    self._allow(DESCRIPTION_FIELD_NAME) \
      .to_be_string() \
      .length_in_range(0, MAX_DESCRIPTION_LENGTH).keep()


class BoxDefinitionValidator(BoxDefinitionOrOutcomeValidator):
  def validate_size(self):
    self._allow(LOG2_SIZE_FIELD_NAME) \
      .to_be_integer() \
      .in_range(MIN_LOG2_SIZE, MAX_LOG2_SIZE).keep()

  def validate_amount_in(self):
    self._allow(AMOUNT_IN_FIELD_NAME).to_be_positive_integer().keep()

  def validate_outcomes(self):
    def buildOutcome(dict):
      valid_fields = OutcomeValidator(dict).run().valid_fields
      return Outcome(**valid_fields)

    self._expect(OUTCOMES_FIELD_NAME) \
      .to_be_array_of(buildOutcome) \
      .length_in_range(MIN_OUTCOMES, MAX_OUTCOMES).keep()

  def _run_validation(self):
    self.validate_title()
    self.validate_description()
    self.validate_size()
    self.validate_amount_in()
    self.validate_outcomes()


class OutcomeValidator(BoxDefinitionOrOutcomeValidator):
  def validate_probability(self):
    self._expect(PROBABILITY_FIELD_NAME).to_be_positive_integer().keep()

  def validate_amount_out(self):
    self._allow(AMOUNT_OUT_FIELD_NAME).to_be_positive_integer().keep()

  def _run_validation(self):
    self.validate_title()
    self.validate_description()
    self.validate_probability()
    self.validate_amount_out()


class BoxDefinitionOperations:
  def __init__(self, **kwargs):
    self.input_fields = kwargs

  def validate(self):
    valid_fields, outcomes = self._validate_inputs()
    box_definition = BoxDefinition(**valid_fields)
    box_definition.outcomes = outcomes
    return box_definition

  def build(self, subscriber):
    valid_fields, outcomes = self._validate_inputs()
    box_definition = BoxDefinition(subscriber=subscriber, **valid_fields)
    box_definition.outcomes = outcomes
    box_definition.save()
    return box_definition

  def _validate_inputs(self):
    valid_fields = BoxDefinitionValidator(self.input_fields).run().valid_fields
    logger.debug(str(valid_fields))
    outcomes = valid_fields.pop(OUTCOMES_FIELD_NAME)
    return valid_fields, outcomes


BOX_DEFINITION_ID_FIELD_NAME = "box_definition_id"
USER_TOKEN_FIELD_NAME = "user_token"
CONSUME_FIELD_NAME = "consume"

MAX_USER_TOKEN = 32


class OutcomeClaimValidator(ItemValidator):
  def validate_box_definition_id(self):
    self._expect(BOX_DEFINITION_ID_FIELD_NAME).to_be_positive_integer().keep()

  def validate_user_token(self):
    self._expect(USER_TOKEN_FIELD_NAME).to_be_string().length_in_range(1, MAX_USER_TOKEN).keep()

  def validate_consume(self):
    self._allow(CONSUME_FIELD_NAME).to_be_bool().keep()

  def _run_validation(self):
    self.validate_box_definition_id()
    self.validate_user_token()
    self.validate_consume()


class SubscriberOperations:
  def __init__(self, subscriber):
    self.subscriber = subscriber

  def claim_outcome(self, **kwargs):
    valid_fields = OutcomeClaimValidator(kwargs).run().valid_fields
    logger.debug(str(valid_fields))
    card = self._get_or_create_card(
        valid_fields.get(BOX_DEFINITION_ID_FIELD_NAME),
        valid_fields.get(USER_TOKEN_FIELD_NAME),
    )
    if valid_fields.get(CONSUME_FIELD_NAME, False):
      card.consumed = True
      card.save()
    return card.outcome

  def _get_or_create_card(self, box_definition_id, user_token):
    card = Card.objects.filter(
        box__box_definition_id=box_definition_id, user_token=user_token,
        consumed=False).select_for_update().first()
    if not card:
      box_definition = self._get_box_definition(box_definition_id)
      BoxDefinitionService(box_definition_id).generate_card(user_token)
    return card

  def _get_box_definition(self, box_definition_id):
    try:
      return BoxDefinition.objects.filter(id=box_definition_id, subscriber=self.subscriber).get()
    except BoxDefinition.DoesNotExist:
      raise ValidationError({"box_definition_id": ["Box definition does not exist"]})
