ARG BASE_IMAGE=python:3.6.7-slim
FROM ${BASE_IMAGE}

WORKDIR /app

ADD requirements.txt .

RUN pip install --no-binary :all: --no-clean --force-reinstall -U pip
RUN pip install --no-binary :all: --no-clean -r requirements.txt

ADD main.py .

ENTRYPOINT python3.6 -u main.py
