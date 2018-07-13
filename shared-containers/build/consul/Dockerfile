ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum clean all && yum install -y which

RUN mkdir /build-output/consul

RUN mkdir -vp /build/gopath/src/github.com/hashicorp/consul
COPY consul-1.1.0.tar.gz /build/
WORKDIR /build
RUN tar -xf consul-1.1.0.tar.gz --strip-components=1 -C /build/gopath/src/github.com/hashicorp/consul/
ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin
WORKDIR /build/gopath/src/github.com/hashicorp/consul
RUN ls -lah
RUN CONSUL_DEV=1 make
RUN cp -vR /build/gopath/src/github.com/hashicorp/consul/bin/consul /build-output/consul/

RUN cd /build-output && \
    tar -I pigz -cf consul.tar.gz consul/

