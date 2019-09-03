ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

ENV GO_VERSION=1.12.9
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_CHECKSUM=50fe8e13592f8cf22304b9c4adfc11849a2c3d281b1d7e09c924ae24874c6daa
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

ENV DEP_VERSION=v0.5.4
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_CHECKSUM=40a78c13753f482208d3f4bea51244ca60a914341050c588dad1f00b1acc116c
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}
ENV DEP_URL=https://github.com/golang/dep/releases/download/${DEP_VERSION}/${DEP_FILE}


RUN mkdir -p /build/dep

RUN curl -Lf ${DEP_URL} -o /build/dep/dep && \
    echo "${DEP_CHECKSUM} */build/dep/dep" | sha256sum -c - && \
    chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/
