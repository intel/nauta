ARG BUILD_IMAGE=golang:1.10.2
ARG BASE_IMAGE=centos:7.4.1708
FROM ${BUILD_IMAGE} as build

RUN mkdir -p ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/experiment-service
WORKDIR ${GOPATH}/src/github.com/NervanaSystems/carbon/applications/experiment-service

ADD glide.yaml glide.yaml
ADD requirements.go requirements.go

RUN glide update --strip-vendor requirements.go

ADD ./ ./

RUN glide update --strip-vendor

RUN go build -o /experiment-service main.go

FROM ${BASE_IMAGE}

COPY --from=build /experiment-service /experiment-service

ENTRYPOINT /experiment-service
