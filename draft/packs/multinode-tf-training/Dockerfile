# Use an official Python runtime as a parent image
FROM tensorflow/tensorflow

RUN mkdir /data
COPY ./data/* /data/

WORKDIR /app

ADD distributed_training.py .
