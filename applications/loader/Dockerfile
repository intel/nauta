ARG BUILD_IMAGE=golang:1.10.2
ARG BASE_IMAGE=centos:7.6.1810

# GLIDE Section
FROM ${BASE_IMAGE} as base
RUN yum update -y && yum install -y wget
RUN mkdir -p /build/glide
ENV GLIDE_VERSION=v0.13.1
ENV GLIDE_ARCH=amd64
ENV GLIDE_OS=linux
ENV GLIDE_FILE=glide-${GLIDE_VERSION}-${GLIDE_OS}-${GLIDE_ARCH}.tar.gz
RUN wget https://github.com/Masterminds/glide/releases/download/${GLIDE_VERSION}/${GLIDE_FILE}
RUN tar -zvxf ${GLIDE_FILE} -C /build/glide
RUN mv /build/glide/${GLIDE_OS}-${GLIDE_ARCH}/glide /bin/glide
RUN chmod 0777 /bin/glide

FROM ${BUILD_IMAGE} as build
COPY --from=base /bin/glide /bin/glide

RUN mkdir -p ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/loader
WORKDIR ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/loader

ADD glide.yaml glide.yaml
ADD requirements.go requirements.go

RUN /bin/glide update --strip-vendor requirements.go

ADD ./ ./

RUN glide update --strip-vendor

ENV GOARCH amd64
ENV GOOS linux
ENV CGO_ENABLED 0


RUN go build -o /loader main.go

FROM ${BASE_IMAGE}

COPY --from=build /loader /loader
