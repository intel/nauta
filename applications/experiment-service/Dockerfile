FROM golang:1.11.5 as build

# DEP Section

RUN mkdir -p /build/dep

ENV DEP_VERSION=v0.4.1
ENV DEP_ARCH=amd64
ENV DEP_OS=linux
ENV DEP_FILE=dep-${DEP_OS}-${DEP_ARCH}

RUN wget https://github.com/golang/dep/releases/download/${DEP_VERSION}/${DEP_FILE}
RUN cp ${DEP_FILE} /build/dep/dep
RUN chmod 0777 /build/dep/dep

ENV PATH=${PATH}:/build/dep/

# Api-server section

ENV APISERVER_BUILDER_VERSION=v1.9-alpha.4
ENV APISERVER_BUILDER_ARCH=amd64
ENV APISERVER_BUILDER_OS=linux

ENV APISERVER_BUILDER_FILE=apiserver-builder-${APISERVER_BUILDER_VERSION}-${APISERVER_BUILDER_OS}-${APISERVER_BUILDER_ARCH}.tar.gz

RUN wget https://github.com/kubernetes-incubator/apiserver-builder/releases/download/${APISERVER_BUILDER_VERSION}/${APISERVER_BUILDER_FILE}
RUN mkdir -p /apiserver-builder
RUN cp ${APISERVER_BUILDER_FILE} /tmp/${APISERVER_BUILDER_FILE}
RUN tar -zvxf /tmp/${APISERVER_BUILDER_FILE} -C /apiserver-builder && rm -rf /tmp/${APISERVER_BUILDER_FILE}

ENV APISERVER_BUILDER_PATH=/apiserver-builder/bin
ENV PATH=${PATH}:${APISERVER_BUILDER_PATH}

# Experiment service section
RUN apt update && apt install -y make

ENV EXP_SVC_PATH=${GOPATH}/src/github.com/nervanasystems/carbon/applications/experiment-service
RUN mkdir -p ${EXP_SVC_PATH}
WORKDIR ${EXP_SVC_PATH}

ADD ./ ./

RUN make build

FROM centos:7.6.1810

COPY --from=build /go/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/apiserver /apiserver
COPY --from=build /go/src/github.com/nervanasystems/carbon/applications/experiment-service/dist/controller-manager /controller-manager
