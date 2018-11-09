ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which git

RUN mkdir /build-output/registry
RUN mkdir -vp /build/gopath/src/

WORKDIR /build
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
RUN go get -v github.com/docker/distribution/cmd/registry
RUN cp /build/gopath/bin/* /build-output/registry/
RUN cd /build-output && \
    tar -I pigz -cf docker-registry.tar.gz registry/
