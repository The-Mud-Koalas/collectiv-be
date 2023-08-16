#!/bin/bash
python manage.py migrate
gunicorn communalspace.wsgi:application --bind=0.0.0.0:8080