FROM python:3.12.7-alpine3.20
ADD ./requirements.txt /app/requirements.txt

RUN apk add build-base
RUN apk add git

RUN pip install --upgrade pip
RUN pip install --no-cache-dir cmake==3.31.0.1 --default-timeout=100 future
RUN pip install --no-cache-dir -r /app/requirements.txt --default-timeout=100 future

ADD ./portfolio /app
WORKDIR /app

# download https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf
# and save it at /app/static/qwen2.5-1.5b-instruct-q5_k_m.gguf

RUN apk add wget
RUN wget https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q5_k_m.gguf -O /app/static/qwen2.5-1.5b-instruct-q5_k_m.gguf

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