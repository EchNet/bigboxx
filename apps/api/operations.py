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


class BoxDefinitionFieldValidator(FieldValidator):
  def to_be_a_valid_title(self):
    return self.to_be_truthy().to_be_string().length_in_range(1, MAX_TITLE_LENGTH)

  def to_be_a_valid_description(self):
    return self.to_be_string().length_in_range(0, MAX_DESCRIPTION_LENGTH)

  def to_be_valid_log2_size(self):
    return self.to_be_integer().in_range(MIN_LOG2_SIZE, MAX_LOG2_SIZE)

  def to_be_valid_outcomes(self):
    def buildOutcome(dict):
      valid_fields = OutcomeValidator(dict).run().valid_fields
      return Outcome(**valid_fields)

    return self.to_be_array_of(buildOutcome).length_in_range(MIN_OUTCOMES, MAX_OUTCOMES)


class BoxDefinitionValidator(ItemValidator):
  @property
  def _field_validator_class(self):
    return BoxDefinitionFieldValidator

  def _run_validation(self):
    self._expect(TITLE_FIELD_NAME).to_be_a_valid_title().keep()
    self._allow(DESCRIPTION_FIELD_NAME).to_be_a_valid_description().keep()
    self._expect(AMOUNT_IN_FIELD_NAME).to_be_positive_integer().keep()
    self._expect(LOG2_SIZE_FIELD_NAME).to_be_valid_log2_size().keep()
    self._expect(OUTCOMES_FIELD_NAME).to_be_valid_outcomes().keep()


class OutcomeValidator(ItemValidator):
  @property
  def _field_validator_class(self):
    return BoxDefinitionFieldValidator

  def _run_validation(self):
    self._expect(TITLE_FIELD_NAME).to_be_a_valid_title().keep()
    self._allow(DESCRIPTION_FIELD_NAME).to_be_a_valid_description().keep()
    self._expect(PROBABILITY_FIELD_NAME).to_be_positive_integer().keep()
    self._allow(AMOUNT_OUT_FIELD_NAME).to_be_positive_integer().keep()


class BoxDefinitionOperations:
  def __init__(self, subscriber, **kwargs):
    self.subscriber = subscriber
    self.input_fields = kwargs

  def validate(self):
    self._validate(False)

  def build(self):
    return self._validate(True)

  def _validate(self, do_build):
    valid_fields = self._validate_inputs()
    outcomes = valid_fields.pop(OUTCOMES_FIELD_NAME)
    box_definition = BoxDefinition(subscriber=self.subscriber, **valid_fields)
    if do_build:
      box_definition.save()
      for outcome in outcomes:
        outcome.box_definition = box_definition
        outcome.save()
      return box_definition
    else:
      box_definition.full_clean()

  def _validate_inputs(self):
    return BoxDefinitionValidator(self.input_fields).run().valid_fields
