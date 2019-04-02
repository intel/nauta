ARG TENSORFLOW_SERVING_BUILD_IMAGE
ARG METRICS_IMAGE=metrics-image
ARG BASE_IMAGE=python:3.6.6
FROM ${TENSORFLOW_SERVING_BUILD_IMAGE} as serving
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_SERVING_VERSION=1.13.0

COPY --from=serving /build-output/tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl /

RUN mkdir /pip3.6
COPY intel_tensorflow-1.13.1-cp36-cp36m-manylinux1_x86_64.whl /pip3.6

COPY --from=serving /build-output/tensorflow_model_server /bin/
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN pip3 install /experiment_metrics-*.tar.gz && \
    rm -rf /experiment_metrics-*.tar.gz

WORKDIR /app

ADD requirements.txt .
RUN pip install --no-binary :all: --no-clean --force-reinstall -U pip
RUN pip install --no-binary :all: --no-clean -r requirements.txt

RUN pip3 install --no-cache-dir --force-reinstall /pip3.6/intel_tensorflow*.whl && \
    pip3 install /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl && \
    rm -rf /pip3.6 /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl

ADD app/ .

ENTRYPOINT python3.6 main.py
