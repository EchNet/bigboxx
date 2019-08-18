web: gunicorn bigboxx.wsgi --max-requests 1200
celery: celery --app=bigboxx worker --beat --loglevel=debug
release: python manage.py migrate --no-input
