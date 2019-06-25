ARG BASE_IMAGE=python:3.6.7-slim
FROM ${BASE_IMAGE}

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-binary :all: --force-reinstall -U pip
RUN pip install --no-binary :all: --no-cache-dir -r requirements.txt

COPY main.py .

ENTRYPOINT python3.6 -u main.py
