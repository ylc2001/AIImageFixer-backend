#!/bin/sh
# python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
gunicorn 'image_restoration.wsgi' -b 0.0.0.0:80 --access-logfile - --log-level info
