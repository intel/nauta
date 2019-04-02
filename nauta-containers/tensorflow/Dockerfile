ARG TENSORFLOW_SERVING_BUILD_IMAGE
ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${TENSORFLOW_SERVING_BUILD_IMAGE} as serving
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}
 
ENV TENSORFLOW_VERSION=1.13.1
ENV TENSORFLOW_SERVING_VERSION=1.13.0

COPY --from=serving /build-output/tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl /
# PIP shall == pip2.7 or pip3.6 and match paths below
RUN mkdir /pip2.7 /pip3.6
COPY intel_tensorflow-1.13.1-cp27-cp27mu-manylinux1_x86_64.whl /pip2.7
COPY intel_tensorflow-1.13.1-cp36-cp36m-manylinux1_x86_64.whl /pip3.6

COPY --from=serving /build-output/tensorflow_model_server /bin/
COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN chmod +x /bin/tensorflow_model_server

RUN ${PIP} install --no-cache-dir --force-reinstall /${PIP}/intel_tensorflow*.whl && \
    ${PIP} install /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl && \
    ${PIP} install --ignore-installed /experiment_metrics-*.tar.gz && \
    rm -rf /pip2.7 /pip3.6 /tensorflow_serving_api-${TENSORFLOW_SERVING_VERSION}-*.whl /experiment_metrics-*.tar.gz

ENV KMP_BLOCKTIME 0
ENV OMP_NUM_THREADS 8
