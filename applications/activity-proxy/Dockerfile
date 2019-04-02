ARG BASE_IMAGE=python:3.6.5
FROM ${BASE_IMAGE}

WORKDIR /app

ADD requirements.txt .

RUN pip install --no-binary :all: --no-clean --force-reinstall -U pip
RUN pip install --no-binary :all: --no-clean -r requirements.txt

ADD app/ .

ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:80 proxy:app
