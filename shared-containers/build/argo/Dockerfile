ARG BASE_IMAGE
FROM ${BASE_IMAGE} as build
ARG ARGO_VERSION="v2.2.1"

RUN yum update -y && yum install -y git make wget syum-utils device-mapper-persistent-data lvm2 && yum clean all


RUN mkdir -p ${GOPATH}/src/github.com/argoproj
WORKDIR ${GOPATH}/src/github.com/argoproj
RUN git clone https://github.com/argoproj/argo.git
WORKDIR ${GOPATH}/src/github.com/argoproj/argo
RUN git checkout ${ARGO_VERSION}

RUN dep ensure -v

ARG MAKE_TARGET="controller executor"
RUN make $MAKE_TARGET
