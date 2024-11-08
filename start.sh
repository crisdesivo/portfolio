#!/bin/sh
gunicorn --bind :${PORT} CristianDesivo.wsgi:application