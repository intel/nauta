ARG BUILD_IMAGE=build-go:1.10.2
ARG BASE_IMAGE=centos:7.6.1810

FROM ${BUILD_IMAGE} as build
ENV EXP_SVC_PATH=${GOPATH}/src/github.com/nervanasystems/carbon/applications/experiment-service
RUN mkdir -p ${EXP_SVC_PATH}
WORKDIR ${EXP_SVC_PATH}

ADD ./ ./

RUN yum -y install make
RUN make build

# Preapre Run Image
FROM ${BASE_IMAGE}

COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/apiserver /apiserver
COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/controller-manager /controller-manager
