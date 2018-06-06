ARG BUILD_IMAGE=go-apiserver-builder:v1.9-alpha.4
ARG BASE_IMAGE=centos:7.4.1708
FROM ${BUILD_IMAGE} as build

ENV EXP_SVC_PATH=${GOPATH}/src/github.com/nervanasystems/carbon/applications/experiment-service
RUN mkdir -p ${EXP_SVC_PATH}
WORKDIR ${EXP_SVC_PATH}

ADD ./ ./

# LOAD vendor data
RUN apiserver-boot update vendor

# Build (generate step should be made before 'docker build' call)
RUN apiserver-boot build executables --generate=false

# Preapre Run Image
FROM ${BASE_IMAGE}

COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/bin/apiserver /apiserver
COPY --from=build /build/work/src/github.com/nervanasystems/carbon/applications/experiment-service/bin/controller-manager /controller-manager
