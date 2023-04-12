web: python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn export_support.wsgi:application --bind=0.0.0.0:$PORT --log-file=-
