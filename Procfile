# web: python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn export_support.wsgi:application --worker-class=gevent --worker-connections=1000 --workers=9 --bind=0.0.0.0:$PORT --log-file=-
#  --log-file=-
web: python manage.py collectstatic -l --noinput && python manage.py migrate && gunicorn export_support.wsgi:application --bind=0.0.0.0:$PORT --log-file=-
