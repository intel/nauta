ARG TENSORFLOW_SERVING_BUILD_IMAGE
ARG TENSORFLOW_BUILD_IMAGE
ARG METRICS_IMAGE=metrics-image
ARG BASE_IMAGE=python:3.6.6
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${TENSORFLOW_SERVING_BUILD_IMAGE} as serving
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_SERVING_VERSION=1.13.0

COPY --from=serving /build-output/tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl /

ENV TENSORFLOW_VERSION=1.13.1
COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /

COPY --from=serving /build-output/tensorflow_model_server /bin/
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN pip3 install /experiment_metrics-*.tar.gz && \
    rm -rf /experiment_metrics-*.tar.gz

WORKDIR /app

ADD requirements.txt .
RUN pip install --no-binary :all: --no-clean --force-reinstall -U pip
RUN pip install --no-binary :all: --no-clean -r requirements.txt

RUN pip3 install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    pip3 install /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl && \
    rm -rf /tensorflow-${TENSORFLOW_VERSION}-*.whl /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl

ADD app/ .

ENTRYPOINT python3.6 main.py
