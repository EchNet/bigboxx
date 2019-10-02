import json

from django.core.validators import ValidationError
from rest_framework.test import APIRequestFactory

from api.views import (
    ClaimOutcomeView,
    CreateOrListBoxDefinitionView,
    RetrieveBoxDefinitionView,
    ValidateBoxDefinitionView,
)
from api.tests.helpers import BaseTestCase


class CreateOrListBoxDefinitionViewTestCase(BaseTestCase):
  URL = "/api/1.0/boxx"
  factory = APIRequestFactory()

  def setUp(self):
    self.view = CreateOrListBoxDefinitionView.as_view()

  def test_no_api_key(self):
    request = self.factory.get(self.URL)
    response = self.view(request)
    self.assertEqual(response.status_code, 401)

  def test_wrong_method(self):
    request = self.factory.put(self.URL)
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 405)

  def test_get(self):
    request = self.factory.get(self.URL)
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.data)
    self.assertEqual(response.data["data"], [])

  def test_post(self):
    data = json.dumps(self.valid_box_definition_input())
    request = self.factory.post(self.URL, data=data, content_type="application/json")
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 201)
    self.assertTrue(response.data)
    self.assertTrue(response.data["data"])


class RetrieveBoxDefinitionViewTestCase(BaseTestCase):
  factory = APIRequestFactory()

  def setUp(self):
    self.view = RetrieveBoxDefinitionView.as_view()

  @staticmethod
  def get_url(id):
    return f"/api/1.0/boxx/{id}"

  def test_no_api_key(self):
    request = self.factory.get(self.get_url(1))
    response = self.view(request)
    self.assertEqual(response.status_code, 401)

  def test_wrong_method(self):
    request = self.factory.post(self.get_url(1))
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 405)

  def test_get_404(self):
    request = self.factory.get(self.get_url(1))
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request, pk=1)
    self.assertEqual(response.status_code, 404)

  def test_get(self):
    subscriber = self.create_subscriber()
    box_definition = self.create_box_definition(subscriber)
    request = self.factory.get(self.get_url(box_definition.pk))
    request.META["HTTP_X_API_KEY"] = self.create_api_key(subscriber)
    response = self.view(request, pk=box_definition.pk)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.data)
    self.assertTrue(response.data["data"])
    self.assertTrue(response.data["data"]["name"])


class ValidateBoxDefinitionViewTestCase(BaseTestCase):
  URL = "/api/1.0/boxx/validate"
  factory = APIRequestFactory()

  def setUp(self):
    self.view = ValidateBoxDefinitionView.as_view()

  def test_wrong_method(self):
    request = self.factory.get(self.URL)
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 405)

  def test_post(self):
    data = json.dumps(self.valid_box_definition_input())
    request = self.factory.post(self.URL, data=data, content_type="application/json")
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.data)
    self.assertTrue(response.data["data"])
    self.assertTrue(response.data["data"]["box_definition"])


class ClaimOutcomeViewTestCase(BaseTestCase):
  URL = "/api/1.0/boxx/claim"
  factory = APIRequestFactory()

  def setUp(self):
    self.view = ClaimOutcomeView.as_view()

  @staticmethod
  def get_url(id):
    return f"/api/1.0/boxx/{id}/claim"

  def test_wrong_method(self):
    request = self.factory.get(self.URL)
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 405)

  def test_wrong_method(self):
    request = self.factory.get(self.get_url(1))
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request)
    self.assertEqual(response.status_code, 405)

  def test_get_404(self):
    request = self.factory.post(self.get_url(1), json.dumps({}), content_type="application/json")
    request.META["HTTP_X_API_KEY"] = self.create_api_key()
    response = self.view(request, pk=1)
    self.assertEqual(response.status_code, 404)

  def test_post(self):
    subscriber = self.create_subscriber()
    box_definition = self.create_box_definition(subscriber)
    self.put_box_definition_into_service(box_definition)
    data = json.dumps(dict(user_token="user1"))
    request = self.factory.post(
        self.get_url(box_definition.id), data=data, content_type="application/json")
    request.META["HTTP_X_API_KEY"] = self.create_api_key(subscriber)
    response = self.view(request, pk=box_definition.pk)
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.data)
    self.assertTrue(response.data["data"])
    self.assertTrue("amount_out" in response.data["data"])
