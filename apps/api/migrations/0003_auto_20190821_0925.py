from django.db import migrations


def update_it(apps, schema_editor):
  Subscriber = apps.get_model('api', 'Subscriber')
  subscriber = Subscriber(name="Tester")
  subscriber.save()

  ApiKey = apps.get_model('api', 'ApiKey')
  api_key = ApiKey(subscriber=subscriber, api_key="$$$$$$$$.TESTER.$$$$$$$$")
  api_key.save()


class Migration(migrations.Migration):

  dependencies = [
      ('api', '0002_auto_20190818_1151'),
  ]

  operations = [
      migrations.RunPython(update_it),
  ]
