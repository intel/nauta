ARG BASE_IMAGE
FROM ${BASE_IMAGE} as build
ARG ARGO_VERSION="v2.2.1"

RUN yum update -y && yum install -y git make wget

WORKDIR /tmp

# Install docker
ENV DOCKER_CHANNEL stable
ENV DOCKER_VERSION 18.09.1
RUN wget -O docker.tgz "https://download.docker.com/linux/static/${DOCKER_CHANNEL}/x86_64/docker-${DOCKER_VERSION}.tgz" && \
   tar --extract --file docker.tgz --strip-components 1 --directory /usr/local/bin/ && \
   rm docker.tgz

RUN go get -v github.com/argoproj/argo && cd ${GOPATH}/src/github.com/argoproj/argo && git checkout ${ARGO_VERSION}

WORKDIR ${GOPATH}/src/github.com/argoproj/argo/

RUN cd ${GOPATH}/src/github.com/argoproj/argo/ && \
    dep ensure -vendor-only && \
    cp -r vendor/* ${GOPATH}/src/

ARG MAKE_TARGET="controller executor"
RUN make $MAKE_TARGET
