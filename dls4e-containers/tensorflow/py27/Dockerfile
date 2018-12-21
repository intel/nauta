ARG BASE_IMAGE
ARG METRICS_IMAGE
FROM ${METRICS_IMAGE} as metrics
FROM ${BASE_IMAGE}

ENV TENSORFLOW_VERSION=1.12.0

COPY --from=metrics /build-output/experiment_metrics-*.tar.gz /

RUN echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list && \
    curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add -

RUN apt-get update && apt-get install tensorflow-model-server=${TENSORFLOW_VERSION}

RUN wget https://storage.googleapis.com/intel-optimized-tensorflow/tensorflow-${TENSORFLOW_VERSION}-cp27-cp27mu-linux_x86_64.whl -O /tensorflow-${TENSORFLOW_VERSION}-cp27-cp27mu-linux_x86_64.whl

RUN pip install --no-cache-dir --force-reinstall /tensorflow-${TENSORFLOW_VERSION}-*.whl && \
    pip install tensorflow-serving-api==${TENSORFLOW_VERSION} && \
    pip install --ignore-installed /experiment_metrics-*.tar.gz && \
    rm -rf /experiment_metrics-*.tar.gz

ENV KMP_BLOCKTIME 0
ENV OMP_NUM_THREADS 8