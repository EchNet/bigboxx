import logging

from django.test import TestCase
from django.conf import settings
from django.core.validators import ValidationError

from api.models import Subscriber
from api.operations import BoxDefinitionOperations


class OperationsTestCase(TestCase):
  def setUp(self):
    logging.disable(logging.CRITICAL)

    self.subscriber = Subscriber(name="Sub")
    self.subscriber.save()

    self.valid_inputs = dict(
        name="Title",
        details="Description",
        log2size=20,
        amount_in=1,
        outcomes=[{
            "name": "jackpot",
            "probability": 1,
            "amount_out": 100000
        }, {
            "name": "nothing",
            "probability": 60
        }])

  def test_validate_box_definition(self):
    BoxDefinitionOperations(**self.valid_inputs).validate()
    # No error thrown

  def test_invalid_box_definition_extra_fields(self):
    self.valid_inputs["extra"] = "Extra"
    with self.assertRaises(ValidationError):
      BoxDefinitionOperations(**self.valid_inputs).validate()

  def test_build_box_definition(self):
    box_definition = BoxDefinitionOperations(**self.valid_inputs).build()
    self.assertTrue(box_definition)
    self.assertEqual(box_definition.name, "Title")
    self.assertEqual(box_definition.details, "Description")
    self.assertEqual(box_definition.log2size, 20)
    self.assertEqual(box_definition.amount_in, 1)
    self.assertEqual(len(box_definition.outcomes), 2)
