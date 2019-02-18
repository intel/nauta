ARG BASE_IMAGE=python:3.6.8
FROM ${BASE_IMAGE}

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app/ .

ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:80 api.main:app
