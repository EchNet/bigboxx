from django.contrib import admin

from api.models import ApiKey


class ApiKeyAdmin(admin.ModelAdmin):
  list_display = ("subscriber_name", "api_key")


admin.site.register(ApiKey, ApiKeyAdmin)
