#!/bin/bash
# build_files.sh — Vercel build script for Django

echo "--- Installing Python dependencies ---"
pip install -r requirements.txt --break-system-packages

echo "--- Collecting static files ---"
python manage.py collectstatic --noinput

echo "--- Running database migrations ---"
python manage.py migrate --noinput

echo "--- Build complete ---"
