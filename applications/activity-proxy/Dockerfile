FROM python:3.6.7-stretch

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app/ .

ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:80 proxy:app
