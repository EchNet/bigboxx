from django.contrib import admin

from api.models import ApiKey


class ApiKeyAdmin(admin.ModelAdmin):
  list_display = ("subscriber", "api_key")


admin.site.register(ApiKey, ApiKeyAdmin)
