ARG BASE_IMAGE=python:3.6.5
FROM ${BASE_IMAGE}

COPY ./ /opt/experiment_metrics

RUN cd /opt/experiment_metrics && python3.6 setup.py sdist
RUN cd /opt/experiment_metrics && pip3.6 install --no-cache-dir ./dist/experiment_metrics-0.0.1.tar.gz

RUN mkdir /build-output/ && cp /opt/experiment_metrics/dist/experiment_metrics-0.0.1.tar.gz /build-output/
