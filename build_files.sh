#!/bin/bash
# build_files.sh — Vercel build script for Django

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt --break-system-packages

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput

echo "--- Running database migrations ---"
python manage.py migrate --noinput

echo "--- Seeding Initial Data ---"
python manage.py seed_slots
python -c "import os, django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_parking.settings'); django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"

echo "--- Build complete ---"
