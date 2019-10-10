"""URL Configuration"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.views.generic import TemplateView

import bigboxx.views as bigboxx_views

urlpatterns = [
    path("", bigboxx_views.HomeView.as_view(), name="home"),
    path("overview", TemplateView.as_view(template_name="overview.html"), name="overview"),
    path("docs", TemplateView.as_view(template_name="docs.html"), name="docs"),
    path("forge", TemplateView.as_view(template_name="forge.html"), name="forge"),
    path("data_admin", TemplateView.as_view(template_name="data_admin.html"), name="data_admin"),
    path("api/1.0/", include("api.urls")),
    path("admin/", admin.site.urls),
]

if settings.SERVE_MEDIA:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
