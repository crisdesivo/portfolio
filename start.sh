#!/bin/sh
gunicorn --bind :${PORT} CristianDesivo.wsgi:application \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -