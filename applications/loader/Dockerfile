ARG BUILD_IMAGE=golang:1.10.2
ARG BASE_IMAGE=centos:7.6.1810

FROM ${BUILD_IMAGE} as build

RUN mkdir -p ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/loader
WORKDIR ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/loader

ADD glide.yaml glide.yaml
ADD requirements.go requirements.go

RUN glide update --strip-vendor requirements.go

ADD ./ ./

RUN glide update --strip-vendor

ENV GOARCH amd64
ENV GOOS linux
ENV CGO_ENABLED 0


RUN go build -o /loader main.go

FROM ${BASE_IMAGE}

COPY --from=build /loader /loader
