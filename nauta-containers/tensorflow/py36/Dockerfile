ARG BASE_IMAGE
ARG METRICS_IMAGE
ARG TENSORFLOW_VERSION

FROM tensorflow/serving:${TENSORFLOW_VERSION} as tensorflow_serving
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /
COPY --from=tensorflow_serving /usr/bin/tensorflow_model_server /usr/bin/

ARG TENSORFLOW_VERSION

RUN wget https://storage.googleapis.com/intel-optimized-tensorflow/tensorflow-${TENSORFLOW_VERSION}-cp36-cp36m-linux_x86_64.whl -O /tensorflow-${TENSORFLOW_VERSION}-cp36-cp36m-linux_x86_64.whl

RUN pip install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    pip install tensorflow-serving-api==${TENSORFLOW_VERSION} && \
    pip install --ignore-installed /experiment_metrics-*.tar.gz && \
    rm -rf /experiment_metrics-*.tar.gz

ENV KMP_BLOCKTIME 0
