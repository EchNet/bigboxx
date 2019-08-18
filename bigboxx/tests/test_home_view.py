from django.test import RequestFactory, TestCase
from django.urls import reverse
from unittest.mock import Mock, patch

from bigboxx.views import HomeView


class HomeViewTestCase(TestCase):
  def setUp(self):
    self.view = HomeView()
    self.request = RequestFactory().get(reverse("home"))
    self.request.user = Mock()
    self.request.user.is_authenticated = False
    self.request.user.is_manager = False
    self.view.request = self.request
