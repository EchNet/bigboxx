from django.conf.urls import url, include
from django.views.generic import RedirectView
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token
from rest_framework_swagger.views import get_swagger_view

import api.views as api_views

urlpatterns = [
    # Methods
    url(r'^boxx/?$', api_views.BoxDefinitionsView.as_view()),
    url(r'^boxx/validate/?$', api_views.ValidateBoxDefinition.as_view()),
    # Authentication
    url(r'^token-refresh/', refresh_jwt_token),
    url(r'^token-verify/', verify_jwt_token),
    url(r'^api-auth/', include("rest_framework.urls", namespace="rest_framework")),
    # Documentation
    url(r'^docs/?$', get_swagger_view(title='API Doc')),
]
