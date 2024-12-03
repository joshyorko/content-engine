#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."

python manage.py makemigrations
python manage.py migrate


# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the Django application using gunicorn
echo "Starting the Django application..."
gunicorn --bind 0.0.0.0:8000 --workers 3 cfehome.wsgi:application

