ARG BASE_IMAGE=tensorflow/tensorflow:1.8.0-py3
FROM ${BASE_IMAGE}

ADD ./ /opt/experiment_metrics

RUN cd /opt/experiment_metrics && python setup.py sdist
RUN cd /opt/experiment_metrics && pip install ./dist/experiment_metrics-0.0.1.tar.gz
