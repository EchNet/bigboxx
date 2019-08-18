"""URL Configuration"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.urls import include, path

import bigboxx.views as bigboxx_views

urlpatterns = [
    path("", bigboxx_views.HomeView.as_view(), name="home"),
    path("api/", include("api.urls")),
    path("admin/", admin.site.urls),
    path("hijack/", include("hijack.urls", namespace="hijack")),
]

if settings.SERVE_MEDIA:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
