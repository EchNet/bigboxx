web: python manage.py runserver 0.0.0.0:$PORT
celery: celery --app=bigboxx worker --beat --loglevel=debug
release: python manage.py migrate --no-input
