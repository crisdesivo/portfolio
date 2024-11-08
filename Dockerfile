FROM python:3.12.7-alpine3.20
ADD ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt 

ADD ./portfolio /app
WORKDIR /app


EXPOSE 8000


CMD ["gunicorn", "--bind", ":8000", "CristianDesivo.wsgi:application"]