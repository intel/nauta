FROM python:3.7

ADD ./ /opt/experiment_metrics

RUN cd /opt/experiment_metrics && python3.7 setup.py sdist
RUN cd /opt/experiment_metrics && pip3.7 install ./dist/experiment_metrics-0.0.1.tar.gz

RUN mkdir /build-output/ && cp /opt/experiment_metrics/dist/experiment_metrics-0.0.1.tar.gz /build-output/
