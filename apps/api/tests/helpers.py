import logging
import random
import string

from django.test import TestCase
from django.core.validators import ValidationError

from api.models import ApiKey, Box, Subscriber
from api.operations import BoxDefinitionOperations
from api.services import BoxDefinitionService


class BaseTestCase(TestCase):
  _subscriber_count = 0
  _box_definition_count = 0

  def setUp(self):
    logging.disable(logging.CRITICAL)

  def valid_subscriber_input(self):
    try:
      return dict(name=f"Subscriber:{self._subscriber_count}")
    finally:
      self._subscriber_count += 1

  def create_subscriber(self, **kwargs):
    params = self.valid_subscriber_input()
    params.update(kwargs)
    subscriber = Subscriber(**params)
    subscriber.save()
    return subscriber

  @staticmethod
  def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

  def create_api_key(self, subscriber=None):
    if subscriber is None:
      subscriber = self.create_subscriber()
    api_key = ApiKey(api_key=self.randomString(), subscriber=subscriber)
    api_key.save()
    return api_key.api_key

  def valid_box_definition_input(self):
    try:
      return dict(
          name=f"BoxDefinition:{self._box_definition_count}",
          details="Description",
          log2size=10,
          amount_in=1,
          outcomes=[{
              "name": "jackpot",
              "probability": 1,
              "amount_out": 1000
          }, {
              "name": "nothing",
              "probability": 60
          }])
    finally:
      self._box_definition_count += 1

  def create_box_definition(self, subscriber=None, **kwargs):
    params = self.valid_box_definition_input()
    params.update(kwargs)
    box_definition = BoxDefinitionOperations(**params).build()
    if subscriber is not None:
      box_definition.subscribers.add(subscriber)
    return box_definition

  def put_box_definition_into_service(self, box_definition):
    box_prospectus = BoxDefinitionService(box_definition).create_random_box_prospectus()
    box_prospectus.save()
    box = Box(
        subscriber=box_definition.subscribers.all()[0],
        series_token='SERIES',
        box_prospectus=box_prospectus,
        random_state=box_prospectus.initial_random_state,
        card_count=0,
    )
    box.save()
