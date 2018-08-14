ARG BASE_IMAGE=python:3.6.5
FROM ${BASE_IMAGE}

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app/ .

ENTRYPOINT python3.6 main.py
