ARG BASE_IMAGE=centos:7.6.1810
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

ENV DEP_VERSION=v0.4.1
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_CHECKSUM=31144e465e52ffbc0035248a10ddea61a09bf28b00784fd3fdd9882c8cbb2315
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}
ENV DEP_URL=https://github.com/golang/dep/releases/download/${DEP_VERSION}/${DEP_FILE}


RUN mkdir -p /build/dep

RUN curl -Lf ${DEP_URL} -o /build/dep/dep && \
    echo "${DEP_CHECKSUM} */build/dep/dep" | sha256sum -c - && \
    chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/
