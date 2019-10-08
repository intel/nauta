ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which && yum clean all

RUN mkdir -p /build-output/consul \
             /build/gopath/src/github.com/hashicorp/consul

ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin

COPY consul-1.4.4.tar.gz /build/

WORKDIR /build

RUN tar -xf consul-1.4.4.tar.gz --strip-components=1 -C /build/gopath/src/github.com/hashicorp/consul/ && \
    cd /build/gopath/src/github.com/hashicorp/consul && \
    CONSUL_DEV=1 make && \
    cp -vR /build/gopath/src/github.com/hashicorp/consul/bin/consul /build-output/consul/ && \
    cd /build-output && \
    tar -I pigz -cf consul.tar.gz consul/

