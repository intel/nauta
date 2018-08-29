ARG BASE_IMAGE=python:3.6.6
FROM ${BASE_IMAGE}

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD main.py .

ENTRYPOINT python3.6 main.py
