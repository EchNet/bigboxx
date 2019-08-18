from django.conf.urls import url, include
from django.views.generic import RedirectView
from rest_framework_jwt.views import refresh_jwt_token, verify_jwt_token
from rest_framework_swagger.views import get_swagger_view

urlpatterns = [
    url(r'^1.0/token-refresh/', refresh_jwt_token),
    url(r'^1.0/token-verify/', verify_jwt_token),
    url(r'^1.0/?$', RedirectView.as_view(url='docs')),
    url(r'^1.0/docs/?$', get_swagger_view(title='API Doc')),
    url(r'^api-auth/', include("rest_framework.urls", namespace="rest_framework")),
]
