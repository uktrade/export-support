web: python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn export_support.wsgi:application --worker-class=gevent --worker-connections=1000 --workers=9 --timeout 0 bind=0.0.0.0:$PORT