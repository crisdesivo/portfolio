#!/bin/sh
gunicorn --bind :${PORT} CristianDesivo.wsgi:application \
    --workers 4 \
    --threads 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -