ARG TENSORFLOW_BUILD_IMAGE
ARG TENSORFLOW_SERVING_BUILD_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${TENSORFLOW_BUILD_IMAGE} as data
FROM ${TENSORFLOW_SERVING_BUILD_IMAGE} as serving
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.9.0

COPY --from=data /build-output/tensorflow-${TENSORFLOW_VERSION}-*.whl /
COPY --from=serving /build-output/tensorflow_serving_api-${TENSORFLOW_VERSION}-*.whl /
COPY --from=serving /build-output/tensorflow_model_server /bin/
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /


RUN chmod +x /bin/tensorflow_model_server

RUN ${PIP} install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    ${PIP} install /tensorflow_serving_api-${TENSORFLOW_VERSION}-*.whl && \
    ${PIP} install --ignore-installed /experiment_metrics-*.tar.gz && \
    rm -rf /tensorflow-${TENSORFLOW_VERSION}-*.whl /tensorflow_serving_api-${TENSORFLOW_VERSION}-*.whl /experiment_metrics-*.tar.gz

ENV KMP_BLOCKTIME 0
ENV OMP_NUM_THREADS 8