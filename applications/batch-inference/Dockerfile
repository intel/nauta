ARG METRICS_IMAGE=metrics-image
ARG BASE_IMAGE=python:3.6.8
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN pip3 install /experiment_metrics-*.tar.gz && \
    rm -rf /experiment_metrics-*.tar.gz

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD app/ .

ENTRYPOINT python3.6 main.py
