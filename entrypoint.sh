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
exec gunicorn -c /app/gunicorn.conf.py yorko-home.wsgi:application

