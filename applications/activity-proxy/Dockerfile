ARG BASE_IMAGE=python:3.6.5
FROM ${BASE_IMAGE}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-binary=:all: --force-reinstall -U pip
RUN pip install --no-binary=:all: --no-cache-dir -r requirements.txt

COPY app/ .

ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:80 proxy:app
