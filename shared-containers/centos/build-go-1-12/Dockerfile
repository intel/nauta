ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# GO Section

RUN mkdir -p /build/work

ENV GO_VERSION=1.12.1
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz

COPY ${GO_FILE} /tmp/${GO_FILE}
RUN tar -zvxf /tmp/${GO_FILE} -C /build && rm -rf /tmp/${GO_FILE}

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin
