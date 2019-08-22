import logging

from api.models import (BoxDefinition, Outcome)
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


class BaseItemValidator(ItemValidator):
  def validate_title(self):
    self._expect(TITLE_FIELD_NAME) \
      .to_be_truthy() \
      .to_be_string() \
      .length_in_range(1, MAX_TITLE_LENGTH).keep()

  def validate_description(self):
    self._allow(DESCRIPTION_FIELD_NAME) \
      .to_be_string() \
      .length_in_range(0, MAX_DESCRIPTION_LENGTH).keep()


class BoxDefinitionValidator(BaseItemValidator):
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


class OutcomeValidator(BaseItemValidator):
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
  def __init__(self, subscriber, **kwargs):
    self.subscriber = subscriber
    self.input_fields = kwargs

  def validate(self):
    return self._validate(False)

  def build(self):
    return self._validate(True)

  def _validate(self, do_build):
    valid_fields = self._validate_inputs()
    outcomes = valid_fields.pop(OUTCOMES_FIELD_NAME)
    logger.debug(str(valid_fields))
    box_definition = BoxDefinition(subscriber=self.subscriber, **valid_fields)
    box_definition.full_clean()
    if do_build:
      box_definition.save()
    box_definition.outcomes = outcomes
    return box_definition

  def _validate_inputs(self):
    return BoxDefinitionValidator(self.input_fields).run().valid_fields
