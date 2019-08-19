Static files during development go here.

During deployment, run python manage.py collectstatic that compiles assets for all apps and moves it to the `static` directory. The `static` directory can then be served by the webserver.

Also see Django settings.
