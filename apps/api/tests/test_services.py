from django.core.validators import ValidationError

from api.services import BoxDefinitionService
from api.tests.helpers import BaseTestCase


class BoxDefinitionServiceTestCase(BaseTestCase):
  def test_free_box_count__zero(self):
    box_definition = self.create_box_definition()
    self.assertEqual(BoxDefinitionService(box_definition).free_box_count(), 0)

  def test_free_box_count__one(self):
    box_definition = self.create_box_definition()
    box = self.create_box(box_definition)
    self.assertEqual(BoxDefinitionService(box_definition).free_box_count(), 1)
