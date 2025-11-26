#!/bin/sh
set -e

echo "Waiting for MySQL..."
until nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
exec gunicorn EscapeSaintonge.wsgi:application --bind 0.0.0.0:8000
