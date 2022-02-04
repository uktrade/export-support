#!/bin/bash
python manage.py collectstatic -l --noinput

if [ "$RUN_MIGRATIONS" ]; then
    python manage.py migrate
fi

gunicorn export_support.wsgi:application --worker-class=gevent --worker-connections=1000 --workers=9 --bind=0.0.0.0:$PORT
