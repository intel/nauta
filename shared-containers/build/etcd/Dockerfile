ARG BASE_IMAGE
FROM ${BASE_IMAGE}

RUN yum update -y && yum install -y which && yum clean all

RUN mkdir -vp /build-output/etcd \
              /build/gopath/src/github.com/coreos/etcd

COPY etcd-v3.3.13.tar.gz /build/

ENV GOPATH=/build/gopath
ENV PATH=$PATH:$GOPATH/bin

WORKDIR /build

RUN tar -xf etcd-v3.3.13.tar.gz --strip-components=1 -C /build/gopath/src/github.com/coreos/etcd && \
    cd /build/gopath/src/github.com/coreos/etcd && \
    make build && \
    cp -vR /build/gopath/src/github.com/coreos/etcd/bin/etcd /build-output/etcd/ && \
    cp -vR /build/gopath/src/github.com/coreos/etcd/bin/etcdctl /build-output/etcd/ && \
    cd /build-output && \
    tar -I pigz -cf etcd.tar.gz etcd/
