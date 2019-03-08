ARG BASE_IMAGE=centos:7.6.1810
FROM ${BASE_IMAGE}

# GO Section

RUN mkdir -p /build/work

ENV GO_VERSION=1.10.2
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz

COPY ${GO_FILE} /tmp/${GO_FILE}
RUN tar -zvxf /tmp/${GO_FILE} -C /build && rm -rf /tmp/${GO_FILE}

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin

# GODEP Section

RUN mkdir -p /build/dep

ENV DEP_VERSION=v0.4.1
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}

COPY ${DEP_FILE} /build/dep/dep

RUN chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/

# GLIDE Section

RUN mkdir -p /build/glide

ENV GLIDE_VERSION=0.13.1
ENV GLIDE_ARCH=amd64
ENV GLIDE_OS=linux
ENV GLIDE_FILE=glide-v${GLIDE_VERSION}-${GLIDE_OS}-${GLIDE_ARCH}

COPY ${GLIDE_FILE} /build/glide/glide

RUN chmod 0777 /build/glide/glide

ENV PATH=${PATH}:/build/glide/
