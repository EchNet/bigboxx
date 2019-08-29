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
        title="Title",
        description="Description",
        log2size=20,
        amount_in=1,
        outcomes=[{
            "title": "jackpot",
            "probability": 1,
            "amount_out": 100000
        }, {
            "title": "nothing",
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
    box_definition = BoxDefinitionOperations(**self.valid_inputs).build(self.subscriber)
    self.assertTrue(box_definition)
    self.assertEqual(box_definition.subscriber, self.subscriber)
    self.assertEqual(box_definition.title, "Title")
    self.assertEqual(box_definition.description, "Description")
    self.assertEqual(box_definition.log2size, 20)
    self.assertEqual(box_definition.amount_in, 1)
    self.assertEqual(len(box_definition.outcomes), 2)
