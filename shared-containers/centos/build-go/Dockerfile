ARG BASE_IMAGE
FROM ${BASE_IMAGE}

# GO Section

RUN mkdir -p /build/work \
             /build/dep \
             /build/glide

ENV GO_VERSION=1.12.9
ENV GO_ARCH=amd64
ENV GO_OS=linux
ENV GO_FILE=go${GO_VERSION}.${GO_OS}-${GO_ARCH}.tar.gz

ADD ${GO_FILE} /build

ENV GOROOT=/build/go
ENV GOPATH=/build/work
ENV PATH=${PATH}:${GOROOT}/bin

# GODEP Section

ENV DEP_VERSION=v0.5.4
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}

COPY ${DEP_FILE} /build/dep/dep

RUN chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/

# GLIDE Section

ENV GLIDE_VERSION=0.13.1
ENV GLIDE_ARCH=amd64
ENV GLIDE_OS=linux
ENV GLIDE_FILE=glide-v${GLIDE_VERSION}-${GLIDE_OS}-${GLIDE_ARCH}

COPY ${GLIDE_FILE} /build/glide/glide

RUN chmod 0777 /build/glide/glide

ENV PATH=${PATH}:/build/glide/
