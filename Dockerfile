FROM python:3.12.7-alpine3.20
ADD ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt 

ADD ./portfolio /app
WORKDIR /app

ARG PORT=8080
EXPOSE ${PORT}

# Add the start script to the working directory
ADD ./start.sh /app/start.sh

# Make the start script executable
RUN chmod +x /app/start.sh

# make migrations
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations --noinput
RUN python manage.py migrate --noinput

CMD ["/app/start.sh"]
# CMD ["gunicorn", "--bind", ${PORT:-8000}, "CristianDesivo.wsgi:application"]