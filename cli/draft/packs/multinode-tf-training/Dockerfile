# Use an official Python runtime as a parent image
FROM dls4e/tensorflow:1.8.0-py3

RUN mkdir /data
COPY ./data/* /data/

WORKDIR /app

ADD distributed_training.py .
