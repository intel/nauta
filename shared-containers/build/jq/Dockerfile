ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN mkdir -vp /build-output/ /build

COPY jq-1.5.tar.gz /build

WORKDIR /build
RUN tar -xvf /build/jq-1.5.tar.gz
WORKDIR /build/jq-1.5/
RUN ./configure
RUN make

RUN cp jq /build-output/jq


