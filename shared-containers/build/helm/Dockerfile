ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# TODO: Compile

RUN mkdir -p /build-output/helm

COPY helm /build-output/helm/

RUN cd /build-output && \
    tar -I pigz -cf helm.tar.gz helm/


