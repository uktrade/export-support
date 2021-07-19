web: python manage.py collectstatic -l --noinput && gunicorn export_support.wsgi:application --worker-class=gevent --worker-connections=1000 --workers=9 --bind=0.0.0.0:$PORT
