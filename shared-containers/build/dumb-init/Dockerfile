ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build-output/ /build

COPY dumb-init-1.2.1.tar.gz /build

WORKDIR /build

RUN tar -xvf /build/dumb-init-1.2.1.tar.gz && \
    cd /build/dumb-init-1.2.1/ && \
# centos does not provide static libraries:
    sed -i 's/-static//g' Makefile && \
    make build && \
    cp dumb-init /build-output/dumb-init && \
    rm -rf /build
