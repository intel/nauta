ARG BASE_IMAGE=centos:7.4.1708
FROM ${BASE_IMAGE}

ENV GO_VERSION=1.10.2
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_CHECKSUM=4b677d698c65370afa33757b6954ade60347aaca310ea92a63ed717d7cb0c2ff
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz
ENV GO_URL=https://dl.google.com/go/${GO_FILE}

RUN mkdir -p /build/work

RUN curl -Lf ${GO_URL} -o /tmp/${GO_FILE} && \
    echo "${GO_CHECKSUM} */tmp/${GO_FILE}" | sha256sum -c - && \
    tar -zvxf /tmp/${GO_FILE} -C /build && \
    rm -rf /tmp/${GO_FILE}

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin

ENV GLIDE_VERSION=v0.13.1
ENV GLIDE_ARCH=amd64
ENV GLIDE_OS=linux
ENV GLIDE_CHECKSUM=c403933503ea40308ecfadcff581ff0dc3190c57958808bb9eed016f13f6f32c
ENV GLIDE_FILE=glide-${GLIDE_VERSION}-${GLIDE_OS}-${GLIDE_ARCH}.tar.gz
ENV GLIDE_URL=https://github.com/Masterminds/glide/releases/download/${GLIDE_VERSION}/${GLIDE_FILE}

RUN mkdir -p /build/glide

RUN curl -Lf ${GLIDE_URL} -o /tmp/${GLIDE_FILE} && \
    echo "${GLIDE_CHECKSUM} */tmp/${GLIDE_FILE}" | sha256sum -c - && \
    tar -zvxf /tmp/${GLIDE_FILE} -C /build/glide && \
    rm -rf /tmp/${GLIDE_FILE}

ENV PATH=${PATH}:/build/glide/${GLIDE_OS}-${GLIDE_ARCH}
